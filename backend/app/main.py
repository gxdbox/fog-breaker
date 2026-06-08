import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import collections, intelligences, alerts, dashboard
from app.services.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _seed_default_collections()
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

app.include_router(collections.router)
app.include_router(intelligences.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


def _seed_default_collections():
    from app.core.database import SessionLocal
    from app.models.models import Collection

    db = SessionLocal()
    try:
        count = db.query(Collection).count()
        if count == 0:
            defaults = [
                Collection(name="HackerNews", source_type="hackernews", category="tech", poll_interval_minutes=30, config={"max_items": 30}),
                Collection(name="微博热搜", source_type="weibo", category="social", poll_interval_minutes=15),
                Collection(name="36kr", source_type="rss", category="business", config={"url": "https://36kr.com/feed"}, poll_interval_minutes=30),
                Collection(name="少数派", source_type="rss", category="tech", config={"url": "https://sspai.com/feed"}, poll_interval_minutes=60),
                Collection(name="InfoQ", source_type="rss", category="tech", config={"url": "https://www.infoq.cn/public/v1/article/list"}, poll_interval_minutes=60),
            ]
            db.add_all(defaults)
            db.commit()
    finally:
        db.close()
