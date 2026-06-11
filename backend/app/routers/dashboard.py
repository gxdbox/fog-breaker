from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Intelligence, AlertLog
from app.models.schemas import DashboardStats, DailyBriefing
from app.analyzers.deepseek import DeepSeekAnalyzer

router = APIRouter(tags=["dashboard"])


@router.get("/stats/", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total = db.query(func.count(Intelligence.id)).filter(Intelligence.is_duplicate == False).scalar()
    today_new = db.query(func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    ).scalar()
    today_analyzed = db.query(func.count(Intelligence.id)).filter(
        Intelligence.is_analyzed == True,
        Intelligence.collected_at >= today,
    ).scalar()
    today_alerts = db.query(func.count(AlertLog.id)).filter(AlertLog.triggered_at >= today).scalar()
    avg_rating = db.query(func.avg(Intelligence.rating)).filter(
        Intelligence.is_analyzed == True,
        Intelligence.is_duplicate == False,
    ).scalar()

    rows = db.query(Intelligence.category, func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
    ).group_by(Intelligence.category).all()
    category_distribution = {row[0]: row[1] for row in rows}

    return DashboardStats(
        total_intelligences=total or 0,
        today_new=today_new or 0,
        today_analyzed=today_analyzed or 0,
        today_alerts=today_alerts or 0,
        avg_rating=round(avg_rating, 2) if avg_rating else None,
        category_distribution=category_distribution,
    )


@router.get("/briefing/", response_model=DailyBriefing)
def get_daily_briefing(db: Session = Depends(get_db)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_intels = (
        db.query(Intelligence)
        .filter(Intelligence.is_duplicate == False, Intelligence.is_analyzed == True, Intelligence.collected_at >= today)
        .order_by(Intelligence.rating.desc().nullslast(), Intelligence.collected_at.desc())
        .limit(30)
        .all()
    )
    all_today = (
        db.query(Intelligence)
        .filter(Intelligence.is_duplicate == False, Intelligence.collected_at >= today)
        .all()
    )

    cat_rows = db.query(Intelligence.category, func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    ).group_by(Intelligence.category).all()
    category_distribution = {row[0]: row[1] for row in cat_rows}

    src_rows = db.query(Intelligence.source_name, func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    ).group_by(Intelligence.source_name).all()
    source_distribution = {row[0]: row[1] for row in src_rows}

    avg_rating = None
    if all_today:
        ratings = [i.rating for i in all_today if i.rating]
        if ratings:
            avg_rating = round(sum(ratings) / len(ratings), 2)

    top_intels = sorted(today_intels, key=lambda x: x.rating or 0, reverse=True)[:5]

    ai_summary = None
    if today_intels and settings.DEEPSEEK_API_KEY:
        analyzer = DeepSeekAnalyzer()
        ai_summary = analyzer.generate_daily_briefing(today_intels)
    elif today_intels:
        top_items = "\n".join(f"- [{i.rating or 0}星] {i.title}" for i in today_intels[:5])
        ai_summary = f"今日共发现 {len(all_today)} 条情报，其中 {len(today_intels)} 条已完成分析。\n\n关键情报：\n{top_items}\n\n行动建议：优先阅读4星以上情报，并对涉及安全、政策或业务机会的信息设置预警。"

    return DailyBriefing(
        date=today.strftime("%Y-%m-%d"),
        total_count=len(all_today),
        avg_rating=avg_rating,
        top_intelligences=top_intels,
        category_distribution=category_distribution,
        source_distribution=source_distribution,
        ai_summary=ai_summary,
    )
