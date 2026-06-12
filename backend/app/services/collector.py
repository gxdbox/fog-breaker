import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.collectors import (
    CBRRateCollector,
    HackerNewsCollector,
    OzonSellerCollector,
    RSSCollector,
    WeiboHotCollector,
)
from app.models.models import Collection, Intelligence
from app.services.vector import VectorService

logger = logging.getLogger(__name__)


class CollectorService:
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService()

    def _get_collector(self, collection: Collection):
        if collection.source_type == "rss":
            url = collection.config.get("url", "")
            language = collection.config.get("language")
            return RSSCollector(name=collection.name, url=url, category=collection.category, language=language)
        if collection.source_type == "hackernews":
            return HackerNewsCollector(max_items=collection.config.get("max_items", 30))
        if collection.source_type == "weibo":
            return WeiboHotCollector()
        if collection.source_type == "cbr_rate":
            return CBRRateCollector(name=collection.name, currencies=collection.config.get("currencies"))
        if collection.source_type == "ozon_seller":
            return OzonSellerCollector(name=collection.name)
        return None

    def collect_all(self):
        collections = self.db.query(Collection).filter(Collection.is_active == True).all()
        total_new = 0
        for col in collections:
            try:
                new_count = self.collect_one(col)
                total_new += new_count
                col.last_fetched_at = datetime.now()
                self.db.commit()
            except Exception as e:
                logger.error(f"Collect error for {col.name}: {e}")
        return total_new

    def collect_one(self, collection: Collection) -> int:
        collector = self._get_collector(collection)
        if not collector:
            return 0

        raw_items = collector.collect()
        new_count = 0
        for raw in raw_items:
            if not raw.title or not raw.content:
                continue
            text_for_dedup = f"{raw.title} {raw.content[:500]}"
            if self.vector_service.is_duplicate(text_for_dedup):
                intel = Intelligence(
                    title=raw.title,
                    content=raw.content,
                    url=raw.url,
                    source_name=raw.source_name,
                    collection_id=collection.id,
                    profile_id=collection.profile_id,
                    category=raw.category,
                    language=raw.language,
                    published_at=raw.published_at,
                    is_duplicate=True,
                )
                self.db.add(intel)
                continue

            intel = Intelligence(
                title=raw.title,
                content=raw.content,
                url=raw.url,
                source_name=raw.source_name,
                collection_id=collection.id,
                profile_id=collection.profile_id,
                category=raw.category,
                language=raw.language,
                published_at=raw.published_at,
            )
            self.db.add(intel)
            self.db.flush()
            self.vector_service.add(intel.id, text_for_dedup)
            new_count += 1

        self.db.commit()
        return new_count
