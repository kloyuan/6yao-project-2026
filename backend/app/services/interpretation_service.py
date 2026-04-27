import json
import re
import logging

from supabase import Client
from fastapi import HTTPException

from app.core import context_loader, prompt_builder, llm_provider

logger = logging.getLogger(__name__)


def get_or_create_interpretation(divination_id: str, db: Client) -> dict:
    existing = (
        db.table("interpretations")
        .select("*")
        .eq("divination_id", divination_id)
        .execute()
    )
    if existing.data:
        return _format(existing.data[0], divination_id)

    ctx = context_loader.load_hexagram_context(divination_id, db)
    system, user_msg = prompt_builder.build_interpretation_prompt(ctx)

    try:
        raw, provider_name = llm_provider.generate_json(
            system, [{"role": "user", "content": user_msg}]
        )
        parsed = _parse_json(raw)
    except Exception as e:
        logger.error("LLM failed for divination %s: %s", divination_id, e)
        return {
            "divination_id": divination_id,
            "error": "AI 解读暂时不可用，请稍后再试。卦象盘面不受影响，可继续查看。",
            "generated_by": "ai",
        }

    record = db.table("interpretations").insert(
        {
            "divination_id": divination_id,
            "language": "zh-CN",
            "summary": parsed.get("summary", ""),
            "base_reading": parsed.get("base_reading", ""),
            "changing_lines_analysis": parsed.get("changing_lines_analysis", ""),
            "changed_hexagram_trend": parsed.get("changed_hexagram_trend", ""),
            "category_advice": parsed.get("category_advice", ""),
            "action_advice": parsed.get("action_advice", []),
            "generated_by": "ai",
            "provider": provider_name,
        }
    ).execute()

    return _format(record.data[0], divination_id)


def _parse_json(raw: str) -> dict:
    logger.debug("Raw LLM response: %s", raw[:500])
    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    # Replace Unicode smart quotes with standard ASCII quotes
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        logger.error("Could not parse LLM response. Raw (first 500 chars): %s", raw[:500])
        raise ValueError("Could not parse LLM response as JSON")


def _format(record: dict, divination_id: str) -> dict:
    return {
        "divination_id": divination_id,
        "summary": record.get("summary"),
        "base_reading": record.get("base_reading"),
        "changing_lines_analysis": record.get("changing_lines_analysis"),
        "changed_hexagram_trend": record.get("changed_hexagram_trend"),
        "category_advice": record.get("category_advice"),
        "action_advice": record.get("action_advice"),
        "generated_by": record.get("generated_by", "ai"),
        "provider": record.get("provider"),
    }
