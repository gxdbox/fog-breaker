from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.analyzers.deepseek import DeepSeekAnalyzer
from app.core.config import settings
from app.core.database import get_db
from app.models.models import AlertLog, Intelligence, Profile
from app.models.schemas import DailyBriefing, DashboardStats

router = APIRouter(tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    intel_q = db.query(Intelligence).filter(Intelligence.is_duplicate == False)
    today_intel_q = intel_q.filter(Intelligence.collected_at >= today)
    if profile_id is not None:
        intel_q = intel_q.filter(Intelligence.profile_id == profile_id)
        today_intel_q = today_intel_q.filter(Intelligence.profile_id == profile_id)

    total_intelligences = intel_q.count()
    today_new = today_intel_q.count()
    today_analyzed = today_intel_q.filter(Intelligence.is_analyzed == True).count()

    alert_q = db.query(AlertLog).filter(AlertLog.triggered_at >= today)
    if profile_id is not None:
        alert_q = alert_q.join(Intelligence, AlertLog.intelligence_id == Intelligence.id).filter(Intelligence.profile_id == profile_id)
    today_alerts = alert_q.count()

    avg_q = db.query(func.avg(Intelligence.rating)).filter(Intelligence.is_analyzed == True)
    if profile_id is not None:
        avg_q = avg_q.filter(Intelligence.profile_id == profile_id)
    avg_rating = avg_q.scalar()

    cat_q = db.query(Intelligence.category, func.count(Intelligence.id)).filter(Intelligence.is_duplicate == False)
    if profile_id is not None:
        cat_q = cat_q.filter(Intelligence.profile_id == profile_id)
    cat_rows = cat_q.group_by(Intelligence.category).all()
    category_distribution = {row[0]: row[1] for row in cat_rows}

    return DashboardStats(
        total_intelligences=total_intelligences,
        today_new=today_new,
        today_analyzed=today_analyzed,
        today_alerts=today_alerts,
        avg_rating=round(avg_rating, 2) if avg_rating else None,
        category_distribution=category_distribution,
    )


@router.get("/briefing/", response_model=DailyBriefing)
def get_daily_briefing(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    analyzed_q = db.query(Intelligence).filter(
        Intelligence.is_duplicate == False,
        Intelligence.is_analyzed == True,
        Intelligence.collected_at >= today,
    )
    all_q = db.query(Intelligence).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    )
    cat_q = db.query(Intelligence.category, func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    )
    src_q = db.query(Intelligence.source_name, func.count(Intelligence.id)).filter(
        Intelligence.is_duplicate == False,
        Intelligence.collected_at >= today,
    )
    if profile_id is not None:
        analyzed_q = analyzed_q.filter(Intelligence.profile_id == profile_id)
        all_q = all_q.filter(Intelligence.profile_id == profile_id)
        cat_q = cat_q.filter(Intelligence.profile_id == profile_id)
        src_q = src_q.filter(Intelligence.profile_id == profile_id)

    today_intels = analyzed_q.order_by(
        Intelligence.rating.desc().nullslast(),
        Intelligence.collected_at.desc(),
    ).limit(30).all()
    all_today = all_q.all()

    category_distribution = {row[0]: row[1] for row in cat_q.group_by(Intelligence.category).all()}
    source_distribution = {row[0]: row[1] for row in src_q.group_by(Intelligence.source_name).all()}

    avg_rating = None
    if all_today:
        ratings = [i.rating for i in all_today if i.rating]
        if ratings:
            avg_rating = round(sum(ratings) / len(ratings), 2)

    top_intels = sorted(today_intels, key=lambda x: x.rating or 0, reverse=True)[:5]

    ai_summary = None
    if today_intels:
        briefing_prompt = None
        if profile_id is not None:
            profile = db.query(Profile).filter(Profile.id == profile_id).first()
            if profile and profile.briefing_prompt:
                briefing_prompt = profile.briefing_prompt
        if settings.DEEPSEEK_API_KEY:
            analyzer = DeepSeekAnalyzer()
            ai_summary = analyzer.generate_daily_briefing(today_intels, prompt_template=briefing_prompt)
        else:
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
