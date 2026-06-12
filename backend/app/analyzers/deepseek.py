import json
import logging
from typing import Optional

from openai import OpenAI

from app.analyzers.prompts import load_prompt
from app.core.config import settings
from app.models.models import Intelligence

logger = logging.getLogger(__name__)


class DeepSeekAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    def analyze(self, intelligence: Intelligence, prompt_template: Optional[str] = None) -> dict:
        template = prompt_template or load_prompt("default")
        prompt = template.format(
            title=intelligence.title,
            content=intelligence.content[:3000],
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            text = resp.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(text)
            action_items = result.get("action_items", [])
            valid_types = {"act", "watch", "opportunity"}
            action_items = [a for a in action_items if isinstance(a, dict) and a.get("type") in valid_types and a.get("text")]
            return {
                "summary": result.get("summary", ""),
                "bullet_summary": result.get("bullet_summary", [])[:5],
                "rating": max(1, min(5, int(result.get("rating", 3)))),
                "rating_reason": result.get("rating_reason", ""),
                "tags": result.get("tags", [])[:5],
                "potential_impact": result.get("potential_impact", ""),
                "plain_explanation": result.get("plain_explanation", ""),
                "action_items": action_items,
                "category": result.get("category", intelligence.category),
            }
        except json.JSONDecodeError:
            logger.warning(f"JSON parse failed for intelligence {intelligence.id}")
            return self._default_result(intelligence)
        except Exception as e:
            logger.error(f"DeepSeek analysis error for intelligence {intelligence.id}: {type(e).__name__}")
            return self._default_result(intelligence)

    def generate_daily_briefing(self, intelligences: list[Intelligence], prompt_template: Optional[str] = None) -> str:
        if not intelligences:
            return "今日无情报数据。"
        items_text = "\n".join(
            f"- [{i.rating}星] {i.title}: {i.summary or i.content[:100]}"
            for i in intelligences[:30]
        )
        template = prompt_template or load_prompt("default_briefing")
        prompt = template.format(items_text=items_text)

        if not settings.DEEPSEEK_API_KEY:
            return self._fallback_briefing(intelligences)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Daily briefing generation error: {type(e).__name__}")
            return self._fallback_briefing(intelligences)

    @staticmethod
    def _fallback_briefing(intelligences: list[Intelligence]) -> str:
        top_items = "\n".join(f"- [{i.rating or 0}星] {i.title}" for i in intelligences[:5])
        return f"今日共发现 {len(intelligences)} 条已分析情报。\n\n关键情报：\n{top_items}\n\n行动建议：优先阅读4星以上情报，并对涉及安全、政策或业务机会的信息设置预警。"

    @staticmethod
    def _default_result(intelligence: Intelligence) -> dict:
        return {
            "summary": "",
            "bullet_summary": [],
            "rating": 3,
            "rating_reason": "分析失败，默认评级",
            "tags": [],
            "potential_impact": "",
            "plain_explanation": "",
            "action_items": [],
            "category": intelligence.category,
        }
