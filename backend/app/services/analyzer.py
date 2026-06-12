import logging

from sqlalchemy.orm import Session

from app.analyzers.deepseek import DeepSeekAnalyzer
from app.models.models import Intelligence, Profile

logger = logging.getLogger(__name__)


class AnalyzerService:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = DeepSeekAnalyzer()

    def analyze_unanalyzed(self, limit: int = 20) -> int:
        intelligences = (
            self.db.query(Intelligence)
            .filter(Intelligence.is_analyzed == False, Intelligence.is_duplicate == False)
            .order_by(Intelligence.collected_at.desc())
            .limit(limit)
            .all()
        )
        analyzed_count = 0
        for intel in intelligences:
            try:
                prompt_template = None
                if intel.profile_id:
                    profile = self.db.query(Profile).filter(Profile.id == intel.profile_id).first()
                    if profile and profile.analyzer_prompt:
                        prompt_template = profile.analyzer_prompt
                result = self.analyzer.analyze(intel, prompt_template=prompt_template)
                intel.summary = result["summary"]
                intel.bullet_summary = result["bullet_summary"]
                intel.rating = result["rating"]
                intel.rating_reason = result["rating_reason"]
                intel.tags = result["tags"]
                intel.potential_impact = result["potential_impact"]
                intel.plain_explanation = result["plain_explanation"]
                intel.action_items = result["action_items"]
                intel.category = result["category"]
                intel.is_analyzed = True
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Analyze error for intelligence {intel.id}: {e}")
        self.db.commit()
        return analyzed_count
