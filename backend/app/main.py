import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import alerts, collections, dashboard, intelligences, profiles
from app.services.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_schema_columns()
    _seed_profiles_and_collections()
    start_scheduler()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(collections.router)
app.include_router(intelligences.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


def _ensure_schema_columns():
    intel_required = {
        "bullet_summary": "JSON",
        "plain_explanation": "TEXT",
        "action_items": "JSON",
        "preference": "INTEGER",
        "profile_id": "INTEGER",
        "language": "VARCHAR(10)",
    }
    collection_required = {
        "profile_id": "INTEGER",
    }
    alert_rule_required = {
        "profile_id": "INTEGER",
    }
    with engine.begin() as conn:
        existing_tables = {row[0] for row in conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "intelligences" in existing_tables:
            cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(intelligences)").fetchall()}
            for name, ctype in intel_required.items():
                if name not in cols:
                    conn.exec_driver_sql(f"ALTER TABLE intelligences ADD COLUMN {name} {ctype}")
        if "collections" in existing_tables:
            cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(collections)").fetchall()}
            for name, ctype in collection_required.items():
                if name not in cols:
                    conn.exec_driver_sql(f"ALTER TABLE collections ADD COLUMN {name} {ctype}")
        if "alert_rules" in existing_tables:
            cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(alert_rules)").fetchall()}
            for name, ctype in alert_rule_required.items():
                if name not in cols:
                    conn.exec_driver_sql(f"ALTER TABLE alert_rules ADD COLUMN {name} {ctype}")


def _seed_profiles_and_collections():
    from app.analyzers.prompts import load_prompt
    from app.core.database import SessionLocal
    from app.models.models import AlertRule, Collection, Profile

    db = SessionLocal()
    try:
        general = db.query(Profile).filter(Profile.name == "通用情报").first()
        if not general:
            general = Profile(
                name="通用情报",
                description="默认画像：HackerNews / 微博 / 科技商业资讯",
                analyzer_prompt=load_prompt("default"),
                briefing_prompt=load_prompt("default_briefing"),
                category_schema=[
                    {"value": "tech", "label": "技术"},
                    {"value": "business", "label": "商业"},
                    {"value": "policy", "label": "政策"},
                    {"value": "social", "label": "社会"},
                    {"value": "general", "label": "综合"},
                ],
                is_default=True,
            )
            db.add(general)
            db.flush()

        ozon = db.query(Profile).filter(Profile.name == "跨境电商-Ozon-家居百货").first()
        if not ozon:
            ozon = Profile(
                name="跨境电商-Ozon-家居百货",
                description="Ozon 平台规则、俄罗斯市场、家居百货品类、物流与汇率",
                analyzer_prompt=load_prompt("ozon_seller"),
                briefing_prompt=load_prompt("ozon_seller_briefing"),
                category_schema=[
                    {"value": "policy", "label": "政策合规"},
                    {"value": "product", "label": "选品机会"},
                    {"value": "logistics", "label": "物流风险"},
                    {"value": "marketing", "label": "营销节点"},
                    {"value": "fx", "label": "汇率"},
                    {"value": "competitor", "label": "竞品动态"},
                    {"value": "general", "label": "综合"},
                ],
            )
            db.add(ozon)
            db.flush()

        # Backfill: 将历史无 profile 的 Collection / Intelligence / AlertRule 归到通用画像
        db.query(Collection).filter(Collection.profile_id.is_(None)).update({"profile_id": general.id})
        from app.models.models import Intelligence
        db.query(Intelligence).filter(Intelligence.profile_id.is_(None)).update({"profile_id": general.id})
        db.query(AlertRule).filter(AlertRule.profile_id.is_(None)).update({"profile_id": general.id})

        if db.query(Collection).filter(Collection.profile_id == general.id).count() == 0:
            db.add_all([
                Collection(name="HackerNews", source_type="hackernews", category="tech", profile_id=general.id, poll_interval_minutes=30, config={"max_items": 30}),
                Collection(name="微博热搜", source_type="weibo", category="social", profile_id=general.id, poll_interval_minutes=15),
                Collection(name="36kr", source_type="rss", category="business", profile_id=general.id, config={"url": "https://36kr.com/feed"}, poll_interval_minutes=30),
                Collection(name="少数派", source_type="rss", category="tech", profile_id=general.id, config={"url": "https://sspai.com/feed"}, poll_interval_minutes=60),
                Collection(name="InfoQ", source_type="rss", category="tech", profile_id=general.id, config={"url": "https://www.infoq.cn/public/v1/article/list"}, poll_interval_minutes=60),
            ])

        _ensure_collection(db, ozon.id, "雨果网", "rss", "general", {"url": "https://www.cifnews.com/feed", "language": "zh"}, 60)
        _ensure_collection(db, ozon.id, "亿邦动力", "rss", "general", {"url": "https://www.ebrun.com/feed/", "language": "zh"}, 60)
        _ensure_collection(db, ozon.id, "俄央行汇率", "cbr_rate", "fx", {"currencies": ["CNY", "USD", "EUR"]}, 240)
        _ensure_collection(db, ozon.id, "Ozon店铺监控", "ozon_seller", "policy", {}, 120)
        _ensure_collection(db, ozon.id, "Vedomosti俄罗斯商业", "rss", "policy", {"url": "https://www.vedomosti.ru/rss/news", "language": "ru"}, 60)
        _ensure_collection(db, ozon.id, "Интерфакс", "rss", "general", {"url": "https://www.interfax.ru/rss.asp", "language": "ru"}, 60)

        if db.query(AlertRule).filter(AlertRule.profile_id == ozon.id).count() == 0:
            db.add_all([
                AlertRule(name="Ozon 合规风险", rule_type="keyword", conditions={"keywords": ["EAC", "认证", "海关", "清关", "Ozon", "罚款", "下架", "违规", "封号"]}, channels=[], profile_id=ozon.id),
                AlertRule(name="俄罗斯市场动态", rule_type="keyword", conditions={"keywords": ["卢布", "中俄", "Ozon", "Wildberries", "俄罗斯", "Москва", "рубль", "таможня"]}, channels=[], profile_id=ozon.id),
                AlertRule(name="家居品类信号", rule_type="keyword", conditions={"keywords": ["家居", "百货", "厨房", "收纳", "家纺", "мебель", "посуда"]}, channels=[], profile_id=ozon.id),
                AlertRule(name="汇率异常", rule_type="keyword", conditions={"keywords": ["卢布贬值", "卢布升值", "汇率", "RUB", "CNY", "рубль"]}, channels=[], profile_id=ozon.id),
            ])

        db.commit()
    finally:
        db.close()


def _ensure_collection(db, profile_id: int, name: str, source_type: str, category: str, config: dict, interval: int):
    from app.models.models import Collection
    exists = db.query(Collection).filter(Collection.profile_id == profile_id, Collection.name == name).first()
    if not exists:
        db.add(Collection(name=name, source_type=source_type, category=category, profile_id=profile_id, config=config, poll_interval_minutes=interval))
