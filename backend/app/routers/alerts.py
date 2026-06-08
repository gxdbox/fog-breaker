from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AlertLog, AlertRule, Intelligence
from app.models.schemas import AlertRuleCreate, AlertRuleOut, AlertLogOut, DashboardStats

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/rules/", response_model=list[AlertRuleOut])
def list_alert_rules(db: Session = Depends(get_db)):
    return db.query(AlertRule).order_by(AlertRule.created_at.desc()).all()


@router.post("/rules/", response_model=AlertRuleOut)
def create_alert_rule(data: AlertRuleCreate, db: Session = Depends(get_db)):
    obj = AlertRule(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/logs/", response_model=list[AlertLogOut])
def list_alert_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(AlertLog).order_by(AlertLog.triggered_at.desc()).offset(skip).limit(limit).all()


@router.patch("/logs/{log_id}/read")
def mark_alert_read(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AlertLog).filter(AlertLog.id == log_id).first()
    if log:
        log.is_read = True
        db.commit()
    return {"ok": True}
