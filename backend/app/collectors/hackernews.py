from datetime import datetime

from app.collectors.base import BaseCollector, RawIntelligence
from app.core.http import get_client


class HackerNewsCollector(BaseCollector):
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, max_items: int = 30):
        self.max_items = max_items

    def collect(self) -> list[RawIntelligence]:
        results = []
        with get_client(timeout=30) as client:
            resp = client.get(f"{self.BASE_URL}/topstories.json")
            story_ids = resp.json()[:self.max_items]

            for sid in story_ids:
                try:
                    item = client.get(f"{self.BASE_URL}/item/{sid}.json").json()
                    if item.get("type") != "story" or item.get("deleted"):
                        continue
                    results.append(RawIntelligence(
                        title=item.get("title", ""),
                        content=item.get("text", "") or item.get("title", ""),
                        url=item.get("url"),
                        source_name="HackerNews",
                        category="tech",
                        published_at=datetime.fromtimestamp(item["time"]) if item.get("time") else None,
                    ))
                except Exception:
                    continue
        return results
