import httpx
from datetime import datetime

from app.collectors.base import BaseCollector, RawIntelligence


class WeiboHotCollector(BaseCollector):
    API_URL = "https://weibo.com/ajax/side/hotSearch"

    def collect(self) -> list[RawIntelligence]:
        results = []
        try:
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                resp = client.get(self.API_URL, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "application/json",
                })
                data = resp.json()
                realtime = data.get("data", {}).get("realtime", [])
                for item in realtime[:30]:
                    word = item.get("word", "")
                    note = item.get("note", word)
                    num = item.get("num", 0)
                    category = "social"
                    label_name = item.get("label_name", "")
                    if "商" in label_name or "财经" in label_name:
                        category = "business"
                    elif "科" in label_name or "数" in label_name:
                        category = "tech"
                    results.append(RawIntelligence(
                        title=note,
                        content=f"微博热搜: {note} (热度: {num})",
                        url=f"https://s.weibo.com/weibo?q=%23{word}%23",
                        source_name="微博热搜",
                        category=category,
                        published_at=datetime.now(),
                    ))
        except Exception:
            pass
        return results
