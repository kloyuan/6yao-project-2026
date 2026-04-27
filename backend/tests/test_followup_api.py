from unittest.mock import patch
from fastapi import HTTPException


def _send(client, divination_id="div-1", message="请问此卦如何？"):
    return client.post(
        f"/divinations/{divination_id}/followup",
        json={"message": message},
    )


# ─── POST /followup ───────────────────────────────────────────────────────────

def test_first_followup_creates_conversation(client):
    with patch("app.api.followup.followup_service.send_message") as mock:
        mock.return_value = {
            "content": "根据卦象...",
            "source_note": "「以上解读基于本次卦象：本卦《乾》变《坤》」",
            "rounds_used": 1,
            "rounds_limit": 20,
        }
        resp = _send(client)

    assert resp.status_code == 200
    data = resp.json()
    assert data["rounds_used"] == 1


def test_rounds_used_increments(client):
    for rounds in range(1, 4):
        with patch("app.api.followup.followup_service.send_message") as mock:
            mock.return_value = {
                "content": "回复",
                "source_note": "「以上解读基于本次卦象：本卦《乾》变《乾》」",
                "rounds_used": rounds,
                "rounds_limit": 20,
            }
            resp = _send(client, message=f"第{rounds}轮追问")
        assert resp.json()["rounds_used"] == rounds


def test_round_20_succeeds(client):
    with patch("app.api.followup.followup_service.send_message") as mock:
        mock.return_value = {
            "content": "最后一轮回复",
            "source_note": "...",
            "rounds_used": 20,
            "rounds_limit": 20,
        }
        resp = _send(client)
    assert resp.status_code == 200
    assert resp.json()["rounds_used"] == 20


def test_round_21_rejected(client):
    with patch(
        "app.api.followup.followup_service.send_message",
        side_effect=HTTPException(status_code=429, detail="已达追问上限 20 轮"),
    ):
        resp = _send(client)
    assert resp.status_code == 429
    assert "上限" in resp.json()["detail"]


def test_assistant_reply_has_source_note(client):
    note = "「以上解读基于本次卦象：本卦《乾》变《坤》」"
    with patch("app.api.followup.followup_service.send_message") as mock:
        mock.return_value = {
            "content": f"解读内容\n{note}",
            "source_note": note,
            "rounds_used": 1,
            "rounds_limit": 20,
        }
        resp = _send(client)
    data = resp.json()
    assert "乾" in data["source_note"] or "本次卦象" in data["source_note"]


# ─── GET /followup ────────────────────────────────────────────────────────────

def test_get_history_returns_messages_in_order(client):
    with patch("app.api.followup.followup_service.get_history") as mock:
        mock.return_value = {
            "messages": [
                {"role": "user", "content": "追问1", "created_at": "2026-01-01T00:00:00"},
                {"role": "assistant", "content": "回答1", "created_at": "2026-01-01T00:01:00"},
            ],
            "rounds_used": 1,
            "rounds_limit": 20,
        }
        resp = client.get("/divinations/div-1/followup")

    assert resp.status_code == 200
    msgs = resp.json()["messages"]
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_get_history_empty_before_first_message(client):
    with patch("app.api.followup.followup_service.get_history") as mock:
        mock.return_value = {"messages": [], "rounds_used": 0, "rounds_limit": 20}
        resp = client.get("/divinations/div-1/followup")

    assert resp.status_code == 200
    assert resp.json()["messages"] == []


def test_get_history_not_found(client):
    with patch(
        "app.api.followup.followup_service.get_history",
        side_effect=HTTPException(status_code=404, detail="Not found"),
    ):
        resp = client.get("/divinations/bad-id/followup")
    assert resp.status_code == 404
