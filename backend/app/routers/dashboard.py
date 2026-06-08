from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Intelligence, AlertLog
from app.models.schemas import DashboardStats

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
