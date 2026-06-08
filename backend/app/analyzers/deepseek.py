import json
import logging

from openai import OpenAI

from app.core.config import settings
from app.models.models import Intelligence

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """你是一名军事情报分析师，请对以下信息进行情报级分析。

信息标题：{title}
信息内容：{content}

请严格按照以下JSON格式输出分析结果（不要输出其他内容）：
{{
    "summary": "一句话摘要，以事实为主，不加观点",
    "rating": 3,
    "rating_reason": "评级理由，1星=噪音信息，2星=低价值，3星=值得关注，4星=重要情报，5星=关键情报",
    "tags": ["标签1", "标签2", "标签3"],
    "potential_impact": "对技术/商业/政策的潜在影响分析",
    "category": "tech/business/policy/social/general"
}}"""


class DeepSeekAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    def analyze(self, intelligence: Intelligence) -> dict:
        prompt = ANALYSIS_PROMPT.format(
            title=intelligence.title,
            content=intelligence.content[:3000],
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            text = resp.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(text)
            return {
                "summary": result.get("summary", ""),
                "rating": max(1, min(5, int(result.get("rating", 3)))),
                "rating_reason": result.get("rating_reason", ""),
                "tags": result.get("tags", [])[:5],
                "potential_impact": result.get("potential_impact", ""),
                "category": result.get("category", intelligence.category),
            }
        except json.JSONDecodeError:
            logger.warning(f"JSON parse failed for intelligence {intelligence.id}")
            return self._default_result(intelligence)
        except Exception as e:
            logger.error(f"DeepSeek analysis error: {e}")
            return self._default_result(intelligence)

    def generate_daily_briefing(self, intelligences: list[Intelligence]) -> str:
        if not intelligences:
            return "今日无情报数据。"
        items_text = "\n".join(
            f"- [{i.rating}星] {i.title}: {i.summary or i.content[:100]}"
            for i in intelligences[:30]
        )
        prompt = f"""你是一名军事情报分析师，请根据今日情报汇总生成一份简明情报简报。

今日情报：
{items_text}

请输出：
1. 今日态势概述（2-3句话总结今日情报态势）
2. 关键情报（列出最重要的3条，说明为什么重要）
3. 风险提示（是否有需要特别关注的趋势或风险）
4. 行动建议（基于今日情报，给出1-2条具体建议）"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Daily briefing generation error: {e}")
            return "简报生成失败，请稍后重试。"

    @staticmethod
    def _default_result(intelligence: Intelligence) -> dict:
        return {
            "summary": "",
            "rating": 3,
            "rating_reason": "分析失败，默认评级",
            "tags": [],
            "potential_impact": "",
            "category": intelligence.category,
        }
