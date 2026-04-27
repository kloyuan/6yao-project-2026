import logging

from supabase import Client
from fastapi import HTTPException

from app.core import context_loader, prompt_builder, llm_provider, conversation_manager

logger = logging.getLogger(__name__)


def send_message(divination_id: str, user_message: str, db: Client) -> dict:
    conv = conversation_manager.get_or_create_conversation(divination_id, db)
    updated_conv = conversation_manager.check_and_increment_rounds(conv, db)

    conversation_manager.add_message(conv["id"], "user", user_message, db)

    ctx = context_loader.load_chat_context(divination_id, db)
    system, messages = prompt_builder.build_followup_prompt(ctx, user_message)

    try:
        reply, _ = llm_provider.generate(system, messages)
    except Exception as e:
        logger.error("LLM failed for followup %s: %s", divination_id, e)
        raise HTTPException(status_code=503, detail="AI 服务暂时不可用，请稍后重试")

    source_note = _extract_source_note(reply)
    conversation_manager.add_message(conv["id"], "assistant", reply, db)

    return {
        "content": reply,
        "source_note": source_note,
        "rounds_used": updated_conv["rounds_used"],
        "rounds_limit": updated_conv["rounds_limit"],
    }


def get_history(divination_id: str, db: Client) -> dict:
    div_check = (
        db.table("divinations").select("id").eq("id", divination_id).execute()
    )
    if not div_check.data:
        raise HTTPException(status_code=404, detail="Divination not found")

    conv_result = (
        db.table("followup_conversations")
        .select("*")
        .eq("divination_id", divination_id)
        .execute()
    )
    if not conv_result.data:
        return {"messages": [], "rounds_used": 0, "rounds_limit": 20}

    conv = conv_result.data[0]
    raw_msgs = conversation_manager.get_messages(conv["id"], db)

    return {
        "messages": [
            {"role": m["role"], "content": m["content"], "created_at": m["created_at"]}
            for m in raw_msgs
        ],
        "rounds_used": conv["rounds_used"],
        "rounds_limit": conv["rounds_limit"],
    }


def _extract_source_note(reply: str) -> str:
    for line in reversed(reply.strip().splitlines()):
        stripped = line.strip()
        if "以上解读基于" in stripped or "本次卦象" in stripped:
            return stripped
    return ""
