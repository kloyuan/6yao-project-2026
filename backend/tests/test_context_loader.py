import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.core.context_loader import load_hexagram_context, load_chat_context


def _make_db(div_data, lines_data=None, conv_data=None, msgs_data=None):
    db = MagicMock()
    call_count = [0]

    results = [
        MagicMock(data=div_data),           # divinations query
        MagicMock(data=lines_data or []),   # divination_lines query
    ]
    if conv_data is not None:
        results.append(MagicMock(data=conv_data))
    if msgs_data is not None:
        results.append(MagicMock(data=msgs_data))

    def execute_side_effect():
        idx = call_count[0]
        call_count[0] += 1
        return results[idx] if idx < len(results) else MagicMock(data=[])

    db.table.return_value = db
    db.select.return_value = db
    db.eq.return_value = db
    db.order.return_value = db
    db.execute.side_effect = lambda: execute_side_effect()
    return db


DIV_COMPLETE = [{
    "id": "div-1",
    "question": "测试问题",
    "category": "事业",
    "timeframe": None,
    "base_hexagram": 1,
    "changed_hexagram": 1,
    "changing_lines": [],
}]

LINES_6 = [
    {"line_number": i, "coin_sum": 7, "line_type": "少阳", "is_changing": False,
     "coin_values": [3, 2, 2]}
    for i in range(1, 7)
]


def test_hexagram_context_has_required_fields():
    db = _make_db(DIV_COMPLETE, LINES_6)
    ctx = load_hexagram_context("div-1", db)

    assert ctx["base_hexagram"] == 1
    assert ctx["changed_hexagram"] == 1
    assert ctx["changing_lines"] == []
    assert ctx["base_hexagram_data"] is not None
    assert ctx["base_hexagram_data"]["name"] == "乾"
    assert ctx["question"] == "测试问题"


def test_hexagram_context_raises_404_when_not_found():
    db = _make_db([])
    with pytest.raises(HTTPException) as exc:
        load_hexagram_context("missing", db)
    assert exc.value.status_code == 404


def test_hexagram_context_raises_422_when_incomplete():
    incomplete_div = [{**DIV_COMPLETE[0], "base_hexagram": None}]
    db = _make_db(incomplete_div, [])
    with pytest.raises(HTTPException) as exc:
        load_hexagram_context("div-1", db)
    assert exc.value.status_code == 422


def test_chat_context_includes_conversation_history():
    conv = [{"id": "conv-1", "rounds_used": 2, "rounds_limit": 20}]
    msgs = [
        {"role": "user", "content": "问题", "created_at": "2026-01-01T00:00:00"},
        {"role": "assistant", "content": "回答", "created_at": "2026-01-01T00:01:00"},
    ]
    db = _make_db(DIV_COMPLETE, LINES_6, conv, msgs)
    ctx = load_chat_context("div-1", db)

    assert ctx["rounds_used"] == 2
    assert len(ctx["messages"]) == 2
    assert ctx["messages"][0]["role"] == "user"


def test_chat_context_empty_when_no_conversation():
    db = _make_db(DIV_COMPLETE, LINES_6, [])
    ctx = load_chat_context("div-1", db)

    assert ctx["rounds_used"] == 0
    assert ctx["messages"] == []
