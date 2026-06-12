from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AlertLog, AlertRule, Intelligence
from app.models.schemas import AlertRuleCreate, AlertRuleOut, AlertLogOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/rules/", response_model=list[AlertRuleOut])
def list_alert_rules(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(AlertRule)
    if profile_id is not None:
        q = q.filter(AlertRule.profile_id == profile_id)
    return q.order_by(AlertRule.created_at.desc()).all()


@router.post("/rules/", response_model=AlertRuleOut)
def create_alert_rule(data: AlertRuleCreate, db: Session = Depends(get_db)):
    obj = AlertRule(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/logs/", response_model=list[AlertLogOut])
def list_alert_logs(
    profile_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(AlertLog)
    if profile_id is not None:
        q = q.join(Intelligence, AlertLog.intelligence_id == Intelligence.id).filter(Intelligence.profile_id == profile_id)
    return q.order_by(AlertLog.triggered_at.desc()).offset(skip).limit(limit).all()


@router.patch("/logs/{log_id}/read")
def mark_alert_read(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AlertLog).filter(AlertLog.id == log_id).first()
    if log:
        log.is_read = True
        db.commit()
    return {"ok": True}
