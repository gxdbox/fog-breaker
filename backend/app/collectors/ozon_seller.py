from __future__ import annotations

import json
import logging
from datetime import datetime

from app.collectors.base import BaseCollector, RawIntelligence
from app.core.config import settings
from app.core.http import get_client

logger = logging.getLogger(__name__)

OZON_API_BASE = "https://api-seller.ozon.ru"


class OzonSellerCollector(BaseCollector):
    """监控 Ozon 店铺：店铺信息、商品列表、评分状态。"""

    def __init__(self, name: str = "Ozon店铺", client_id: str = "", api_key: str = ""):
        self.name = name
        self.client_id = client_id or settings.OZON_CLIENT_ID
        self.api_key = api_key or settings.OZON_API_KEY

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _post(self, path: str, body: dict) -> dict:
        with get_client(timeout=30, extra_headers=self._headers) as client:
            resp = client.post(f"{OZON_API_BASE}{path}", json=body)
            if resp.status_code >= 400:
                logger.warning(f"Ozon API error {resp.status_code} on {path}: {resp.text[:200]}")
                return {}
            return resp.json()

    def collect(self) -> list[RawIntelligence]:
        if not self.client_id or not self.api_key:
            logger.info("Ozon API credentials not configured, skipping")
            return []

        results = []
        now = datetime.now()

        seller = self._post("/v1/seller/info", {})
        if seller:
            company = seller.get("company", {})
            shop_name = company.get("name", "Ozon店铺")
            legal = company.get("legal_name", "")
            currency = company.get("currency", "")
            country = company.get("country", "")

            lines = [f"店铺名称: {shop_name}", f"公司: {legal}", f"结算币种: {currency}", f"注册地: {country}"]

            ratings = seller.get("ratings", [])
            for r in ratings:
                name = r.get("name", "")
                status = r.get("status", "")
                val = r.get("current_value")
                if val is not None:
                    lines.append(f"  {name}: {val} ({status})")
                elif status and status != "UNKNOWN":
                    lines.append(f"  {name}: {status}")

            results.append(RawIntelligence(
                title=f"Ozon店铺: {shop_name} - {legal}",
                content="\n".join(lines),
                url="https://seller.ozon.ru/app/dashboard",
                source_name=self.name,
                category="policy",
                language="ru",
                published_at=now,
            ))

        products = self._post("/v3/product/list", {"filter": {"visibility": "ALL"}, "limit": 100, "last_id": ""})
        if products:
            items = products.get("result", {}).get("items", [])
            total = products.get("result", {}).get("total", len(items))
            active = sum(1 for i in items if not i.get("archived"))
            archived = sum(1 for i in items if i.get("archived"))
            has_fbo = sum(1 for i in items if i.get("has_fbo_stocks"))
            has_fbs = sum(1 for i in items if i.get("has_fbs_stocks"))

            results.append(RawIntelligence(
                title=f"Ozon商品: 共{total}件, 在售{active}件, 归档{archived}件",
                content=f"商品统计（前100件）:\n- 在售: {active}\n- 归档: {archived}\n- FBO在库: {has_fbo}\n- FBS有货: {has_fbs}",
                url="https://seller.ozon.ru/app/products",
                source_name=self.name,
                category="product",
                language="ru",
                published_at=now,
            ))

        if not results:
            results.append(RawIntelligence(
                title=f"Ozon店铺监控: {self.name}",
                content=f"{now.strftime('%Y-%m-%d %H:%M')} 检查完成，无法获取数据。",
                url="https://seller.ozon.ru/app/dashboard",
                source_name=self.name,
                category="policy",
                language="ru",
                published_at=now,
            ))

        return results
