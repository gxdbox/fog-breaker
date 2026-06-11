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
    "summary": "一句话摘要，10字以内，提炼核心事实",
    "bullet_summary": ["要点1", "要点2", "要点3"],
    "rating": 3,
    "rating_reason": "评级理由，1星=噪音信息，2星=低价值，3星=值得关注，4星=重要情报，5星=关键情报",
    "tags": ["标签1", "标签2", "标签3"],
    "potential_impact": "对技术/商业/政策的潜在影响分析",
    "plain_explanation": "用大白话解释这条情报在说什么，让非专业人士也能看懂，必要时用日常类比",
    "action_items": [
        {{"type": "act", "text": "具体的立即行动建议"}},
        {{"type": "watch", "text": "需要持续关注的事项"}},
        {{"type": "opportunity", "text": "可以抓住的机会"}}
    ],
    "category": "tech/business/policy/social/general"
}}

要求：
- bullet_summary: 3-5个核心要点，每个要点一句话，用事实不用观点
- plain_explanation: 用最通俗的语言解释，避免专业术语，如果涉及专业概念用类比说明
- action_items: 根据情报内容给出可执行的建议，type只能是act/watch/opportunity之一，如果没有合适的建议对应类型可以不填该类型"""


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

        if not settings.DEEPSEEK_API_KEY:
            top_items = "\n".join(f"- [{i.rating or 0}星] {i.title}" for i in intelligences[:5])
            return f"今日共发现 {len(intelligences)} 条已分析情报。\n\n关键情报：\n{top_items}\n\n行动建议：优先阅读4星以上情报，并对涉及安全、政策或业务机会的信息设置预警。"

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
