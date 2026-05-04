from __future__ import annotations
from typing import Optional

from supabase import Client
from fastapi import HTTPException

from app.core.rules_engine import map_coin, generate_hexagram
from app.core.hexagram_data import get_hexagram_by_id
from app.core.najia_engine import get_najia, compute_time_context, compute_line_time_state
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
    cast_datetime: Optional[str] = None,
    timezone: Optional[str] = None,
) -> dict:
    div_result = (
        db.table("divinations").select("*").eq("id", divination_id).execute()
    )
    if not div_result.data:
        raise HTTPException(status_code=404, detail="Divination not found")

    div = div_result.data[0]
    coin_sum = sum(coin_values)
    line_type, is_changing = map_coin(coin_sum)

    # On first line: record cast time and derive time context
    if line_number == 1 and cast_datetime and timezone:
        try:
            time_ctx = compute_time_context(cast_datetime, timezone)
            db.table("divinations").update({
                "cast_datetime": cast_datetime,
                "timezone": timezone,
                **time_ctx,
            }).eq("id", divination_id).execute()
            div.update(time_ctx)
        except Exception:
            pass  # Time context is best-effort; don't fail the line submission

    # Derive NaJia if hexagram is already known (line 6 finalizes it) or we can look ahead
    # For lines 1-5 we don't know the final hexagram yet, so branch/element stored after finalize
    line_record: dict = {
        "divination_id": divination_id,
        "line_number": line_number,
        "coin_values": coin_values,
        "coin_sum": coin_sum,
        "line_type": line_type,
        "is_changing": is_changing,
    }
    db.table("divination_lines").insert(line_record).execute()

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
    base_id = hexagram["base_hexagram"]

    db.table("divinations").update(
        {
            "base_hexagram": base_id,
            "changed_hexagram": hexagram["changed_hexagram"],
            "changing_lines": hexagram["changing_lines"],
        }
    ).eq("id", divination_id).execute()

    # Write NaJia (branch/element) to each line now that we know the hexagram
    try:
        base_data = get_hexagram_by_id(base_id)
        trigrams = base_data["trigrams"]
        for line in lines:
            branch, element = get_najia(trigrams, line["line_number"])
            db.table("divination_lines").update(
                {"branch": branch, "element": element}
            ).eq("id", line["id"]).execute()
    except Exception:
        pass  # NaJia is best-effort


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

    # Attach runtime LineTimeState if time context is available
    month_branch = div.get("month_branch")
    day_branch = div.get("day_branch")
    void_branches = div.get("void_branches") or []

    enriched_lines = []
    for line in lines:
        line_dict = dict(line)
        branch = line_dict.get("branch")
        if branch and month_branch and day_branch:
            try:
                line_dict["time_state"] = compute_line_time_state(
                    branch=branch,
                    month_branch=month_branch,
                    day_branch=day_branch,
                    void_branches=void_branches,
                    is_changing=line_dict.get("is_changing", False),
                )
            except Exception:
                line_dict["time_state"] = None
        else:
            line_dict["time_state"] = None
        enriched_lines.append(line_dict)

    return {
        "divination_id": divination_id,
        "question": div["question"],
        "category": div["category"],
        "timeframe": div.get("timeframe"),
        "base_hexagram": base_id,
        "changed_hexagram": changed_id,
        "changing_lines": div.get("changing_lines") or [],
        "lines": enriched_lines,
        "base_hexagram_data": base_data,
        "changed_hexagram_data": changed_data,
        "time_context": {
            "cast_datetime": div.get("cast_datetime"),
            "timezone": div.get("timezone"),
            "month_branch": month_branch,
            "day_stem_branch": div.get("day_stem_branch"),
            "day_branch": day_branch,
            "void_branches": void_branches,
        },
    }
