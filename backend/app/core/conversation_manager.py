from supabase import Client
from fastapi import HTTPException

ROUNDS_LIMIT = 20


def get_or_create_conversation(divination_id: str, db: Client) -> dict:
    result = (
        db.table("followup_conversations")
        .select("*")
        .eq("divination_id", divination_id)
        .execute()
    )
    if result.data:
        return result.data[0]

    new_result = db.table("followup_conversations").insert(
        {
            "divination_id": divination_id,
            "rounds_used": 0,
            "rounds_limit": ROUNDS_LIMIT,
        }
    ).execute()
    return new_result.data[0]


def check_and_increment_rounds(conversation: dict, db: Client) -> dict:
    if conversation["rounds_used"] >= conversation["rounds_limit"]:
        raise HTTPException(
            status_code=429,
            detail=f"已达追问上限 {conversation['rounds_limit']} 轮，无法继续追问",
        )

    updated = (
        db.table("followup_conversations")
        .update({"rounds_used": conversation["rounds_used"] + 1})
        .eq("id", conversation["id"])
        .execute()
    )
    return updated.data[0]


def add_message(conversation_id: str, role: str, content: str, db: Client) -> dict:
    result = db.table("followup_messages").insert(
        {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        }
    ).execute()
    return result.data[0]


def get_messages(conversation_id: str, db: Client) -> list[dict]:
    result = (
        db.table("followup_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return result.data or []
