from __future__ import annotations

import logging
from datetime import date, datetime
from xml.etree import ElementTree as ET

from app.collectors.base import BaseCollector, RawIntelligence
from app.core.http import get_client

logger = logging.getLogger(__name__)

CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


class CBRRateCollector(BaseCollector):
    """俄罗斯央行每日汇率（基准 RUB），抓取指定币种相对 RUB 的汇率。

    输出一条情报，title 含主要币种汇率，category=fx。
    若该日已抓过且数值无变化，无需自然处理（去重在上层 vector_service 完成）。
    """

    def __init__(self, name: str = "俄央行汇率", currencies: list[str] | None = None):
        self.name = name
        self.currencies = currencies or ["CNY", "USD", "EUR"]

    def collect(self) -> list[RawIntelligence]:
        try:
            with get_client(timeout=15) as client:
                resp = client.get(CBR_URL)
                xml_text = resp.content.decode("windows-1251")
            root = ET.fromstring(xml_text)
        except Exception as e:
            logger.error(f"CBR rate fetch failed: {type(e).__name__}: {e}")
            return []

        date_str = root.attrib.get("Date") or date.today().strftime("%d.%m.%Y")
        try:
            published_at = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            published_at = datetime.now()

        rates: dict[str, float] = {}
        nominals: dict[str, int] = {}
        for valute in root.findall("Valute"):
            code = valute.findtext("CharCode")
            if code in self.currencies:
                value_text = (valute.findtext("Value") or "0").replace(",", ".")
                nominal_text = valute.findtext("Nominal") or "1"
                try:
                    rates[code] = float(value_text)
                    nominals[code] = int(nominal_text)
                except ValueError:
                    continue

        if not rates:
            return []

        parts = []
        for code in self.currencies:
            if code in rates:
                per_unit = rates[code] / nominals[code]
                parts.append(f"1 {code} = {per_unit:.4f} RUB")
        title = f"俄央行汇率 {date_str}: " + " | ".join(parts)
        content = (
            f"俄罗斯央行公布 {date_str} 官方汇率（基准币种 RUB）：\n"
            + "\n".join(
                f"- {nominals[code]} {code} = {rates[code]:.4f} RUB（折算：1 {code} = {rates[code] / nominals[code]:.4f} RUB）"
                for code in self.currencies
                if code in rates
            )
            + "\n\n数据来源：俄罗斯央行 cbr.ru 每日基准汇率。"
        )

        return [RawIntelligence(
            title=title,
            content=content,
            url=CBR_URL,
            source_name=self.name,
            category="fx",
            language="ru",
            published_at=published_at,
        )]
