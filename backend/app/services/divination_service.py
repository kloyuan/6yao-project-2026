from supabase import Client
from fastapi import HTTPException

from app.core.rules_engine import map_coin, generate_hexagram
from app.core.hexagram_data import get_hexagram_by_id
from app.models import CreateDivinationRequest


def create_divination(req: CreateDivinationRequest, db: Client) -> str:
    result = db.table("divinations").insert(
        {
            "question": req.question,
            "category": req.category,
            "timeframe": req.timeframe,
            "session_token": req.session_token,
        }
    ).execute()
    return result.data[0]["id"]


def submit_line(
    divination_id: str,
    line_number: int,
    coin_values: list[int],
    db: Client,
) -> dict:
    div_check = (
        db.table("divinations").select("id").eq("id", divination_id).execute()
    )
    if not div_check.data:
        raise HTTPException(status_code=404, detail="Divination not found")

    coin_sum = sum(coin_values)
    line_type, is_changing = map_coin(coin_sum)

    db.table("divination_lines").insert(
        {
            "divination_id": divination_id,
            "line_number": line_number,
            "coin_values": coin_values,
            "coin_sum": coin_sum,
            "line_type": line_type,
            "is_changing": is_changing,
        }
    ).execute()

    if line_number == 6:
        _finalize_hexagram(divination_id, db)

    return {
        "line_number": line_number,
        "coin_values": coin_values,
        "coin_sum": coin_sum,
        "line_type": line_type,
        "is_changing": is_changing,
    }


def _finalize_hexagram(divination_id: str, db: Client) -> None:
    lines_result = (
        db.table("divination_lines")
        .select("*")
        .eq("divination_id", divination_id)
        .order("line_number")
        .execute()
    )
    lines = lines_result.data or []
    if len(lines) < 6:
        return

    coin_sums = [line["coin_sum"] for line in lines]
    hexagram = generate_hexagram(coin_sums)

    db.table("divinations").update(
        {
            "base_hexagram": hexagram["base_hexagram"],
            "changed_hexagram": hexagram["changed_hexagram"],
            "changing_lines": hexagram["changing_lines"],
        }
    ).eq("id", divination_id).execute()


def get_result(divination_id: str, db: Client) -> dict:
    div_result = (
        db.table("divinations").select("*").eq("id", divination_id).execute()
    )
    if not div_result.data:
        raise HTTPException(status_code=404, detail="Divination not found")

    div = div_result.data[0]

    lines_result = (
        db.table("divination_lines")
        .select("*")
        .eq("divination_id", divination_id)
        .order("line_number")
        .execute()
    )
    lines = lines_result.data or []

    base_id = div.get("base_hexagram")
    changed_id = div.get("changed_hexagram")
    base_data = get_hexagram_by_id(base_id) if base_id else None
    changed_data = (
        get_hexagram_by_id(changed_id)
        if changed_id and changed_id != base_id
        else None
    )

    return {
        "divination_id": divination_id,
        "question": div["question"],
        "category": div["category"],
        "timeframe": div.get("timeframe"),
        "base_hexagram": base_id,
        "changed_hexagram": changed_id,
        "changing_lines": div.get("changing_lines") or [],
        "lines": lines,
        "base_hexagram_data": base_data,
        "changed_hexagram_data": changed_data,
    }
