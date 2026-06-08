import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import AlertLog, AlertRule, Intelligence

logger = logging.getLogger(__name__)


class AlerterService:
    def __init__(self, db: Session):
        self.db = db

    def check_alerts(self, intelligence: Intelligence):
        rules = self.db.query(AlertRule).filter(AlertRule.is_active == True).all()
        for rule in rules:
            triggered = False
            message = ""
            if rule.rule_type == "keyword":
                keywords = rule.conditions.get("keywords", [])
                for kw in keywords:
                    if kw.lower() in intelligence.title.lower() or kw.lower() in intelligence.content.lower():
                        triggered = True
                        message = f"关键词「{kw}」匹配: {intelligence.title}"
                        break
            if triggered:
                log = AlertLog(
                    alert_rule_id=rule.id,
                    intelligence_id=intelligence.id,
                    message=message,
                )
                self.db.add(log)
        self.db.commit()

    def check_recent_unchecked(self):
        recent = (
            self.db.query(Intelligence)
            .filter(Intelligence.is_analyzed == True)
            .order_by(Intelligence.collected_at.desc())
            .limit(100)
            .all()
        )
        for intel in recent:
            existing = self.db.query(AlertLog).filter(AlertLog.intelligence_id == intel.id).first()
            if not existing:
                self.check_alerts(intel)
