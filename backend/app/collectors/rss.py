import feedparser
from datetime import datetime

from app.collectors.base import BaseCollector, RawIntelligence


class RSSCollector(BaseCollector):
    def __init__(self, name: str, url: str, category: str = "general"):
        self.name = name
        self.url = url
        self.category = category

    def collect(self) -> list[RawIntelligence]:
        feed = feedparser.parse(self.url)
        results = []
        for entry in feed.entries:
            content = ""
            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            elif hasattr(entry, "description"):
                content = entry.description

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            results.append(RawIntelligence(
                title=entry.get("title", ""),
                content=content,
                url=entry.get("link"),
                source_name=self.name,
                category=self.category,
                published_at=published,
            ))
        return results
