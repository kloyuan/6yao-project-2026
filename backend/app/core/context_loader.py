from supabase import Client
from fastapi import HTTPException
from app.core.hexagram_data import get_hexagram_by_id


def load_hexagram_context(divination_id: str, db: Client) -> dict:
    """Load context for InterpretationService."""
    result = db.table("divinations").select("*").eq("id", divination_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Divination not found")

    div = result.data[0]
    if not div.get("base_hexagram"):
        raise HTTPException(
            status_code=422,
            detail="Divination is not complete yet (all 6 lines required)",
        )

    lines_result = (
        db.table("divination_lines")
        .select("*")
        .eq("divination_id", divination_id)
        .order("line_number")
        .execute()
    )
    lines = lines_result.data or []

    base_data = get_hexagram_by_id(div["base_hexagram"])
    changed_id = div["changed_hexagram"]
    changed_data = get_hexagram_by_id(changed_id) if changed_id != div["base_hexagram"] else None

    return {
        "divination_id": divination_id,
        "question": div["question"],
        "category": div["category"],
        "timeframe": div.get("timeframe"),
        "base_hexagram": div["base_hexagram"],
        "changed_hexagram": changed_id,
        "changing_lines": div.get("changing_lines") or [],
        "base_hexagram_data": base_data,
        "changed_hexagram_data": changed_data,
        "lines": lines,
        "month_branch": div.get("month_branch"),
        "day_stem_branch": div.get("day_stem_branch"),
        "day_branch": div.get("day_branch"),
        "void_branches": div.get("void_branches") or [],
        "cast_datetime": div.get("cast_datetime"),
    }


def load_chat_context(divination_id: str, db: Client) -> dict:
    """Load context for FollowupService (hexagram + conversation history)."""
    ctx = load_hexagram_context(divination_id, db)

    conv_result = (
        db.table("followup_conversations")
        .select("*")
        .eq("divination_id", divination_id)
        .execute()
    )
    if conv_result.data:
        conv = conv_result.data[0]
        msgs_result = (
            db.table("followup_messages")
            .select("*")
            .eq("conversation_id", conv["id"])
            .order("created_at")
            .execute()
        )
        ctx["conversation_id"] = conv["id"]
        ctx["rounds_used"] = conv["rounds_used"]
        ctx["rounds_limit"] = conv["rounds_limit"]
        ctx["messages"] = msgs_result.data or []
    else:
        ctx["conversation_id"] = None
        ctx["rounds_used"] = 0
        ctx["rounds_limit"] = 20
        ctx["messages"] = []

    return ctx
