import feedparser
from datetime import datetime
from typing import Optional

from app.collectors.base import BaseCollector, RawIntelligence
from app.core.http import get_client


class RSSCollector(BaseCollector):
    def __init__(self, name: str, url: str, category: str = "general", language: Optional[str] = None):
        self.name = name
        self.url = url
        self.category = category
        self.language = language

    def collect(self) -> list[RawIntelligence]:
        with get_client(timeout=30) as client:
            resp = client.get(self.url)
            resp.encoding = resp.charset_encoding or "utf-8"
            feed = feedparser.parse(resp.text)
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
                language=self.language,
                published_at=published,
            ))
        return results
