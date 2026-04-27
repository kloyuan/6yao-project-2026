from unittest.mock import patch, MagicMock
import pytest


BASE_REQUEST = {
    "question": "我的事业前景如何？",
    "category": "事业",
    "session_token": "test-session-token",
}


# ─── POST /divinations ────────────────────────────────────────────────────────

def test_create_divination_returns_id(client):
    with patch("app.api.divinations.divination_service.create_divination") as mock:
        mock.return_value = "div-abc-123"
        resp = client.post("/divinations", json=BASE_REQUEST)
    assert resp.status_code == 200
    assert resp.json()["divination_id"] == "div-abc-123"


def test_create_divination_empty_question_rejected(client):
    resp = client.post("/divinations", json={**BASE_REQUEST, "question": ""})
    assert resp.status_code == 422


def test_create_divination_invalid_category_rejected(client):
    resp = client.post("/divinations", json={**BASE_REQUEST, "category": "无效分类"})
    assert resp.status_code == 422


# ─── POST /divinations/{id}/lines ────────────────────────────────────────────

def test_submit_line_lao_yang(client):
    with patch("app.api.divinations.divination_service.submit_line") as mock:
        mock.return_value = {
            "line_number": 1,
            "coin_values": [3, 3, 3],
            "coin_sum": 9,
            "line_type": "老阳",
            "is_changing": True,
        }
        resp = client.post("/divinations/div-1/lines", json={
            "line_number": 1,
            "coin_values": [3, 3, 3],
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["line_type"] == "老阳"
    assert data["is_changing"] is True
    assert data["coin_sum"] == 9


def test_submit_line_shao_yin(client):
    with patch("app.api.divinations.divination_service.submit_line") as mock:
        mock.return_value = {
            "line_number": 2,
            "coin_values": [3, 3, 2],
            "coin_sum": 8,
            "line_type": "少阴",
            "is_changing": False,
        }
        resp = client.post("/divinations/div-1/lines", json={
            "line_number": 2,
            "coin_values": [3, 3, 2],
        })
    assert resp.status_code == 200
    assert resp.json()["line_type"] == "少阴"
    assert resp.json()["is_changing"] is False


def test_submit_line_invalid_coin_value_rejected(client):
    resp = client.post("/divinations/div-1/lines", json={
        "line_number": 1,
        "coin_values": [1, 2, 3],  # 1 is invalid
    })
    assert resp.status_code == 422


def test_submit_line_not_found(client):
    from fastapi import HTTPException
    with patch("app.api.divinations.divination_service.submit_line",
               side_effect=HTTPException(status_code=404, detail="Divination not found")):
        resp = client.post("/divinations/nonexistent/lines", json={
            "line_number": 1,
            "coin_values": [3, 2, 3],
        })
    assert resp.status_code == 404


# ─── GET /divinations/{id}/result ────────────────────────────────────────────

def test_get_result_complete_board(client):
    with patch("app.api.divinations.divination_service.get_result") as mock:
        mock.return_value = {
            "divination_id": "div-1",
            "question": "测试问题",
            "category": "事业",
            "timeframe": None,
            "base_hexagram": 1,
            "changed_hexagram": 2,
            "changing_lines": [1, 2, 3, 4, 5, 6],
            "lines": [],
            "base_hexagram_data": {"hexagram_id": 1, "name": "乾"},
            "changed_hexagram_data": {"hexagram_id": 2, "name": "坤"},
        }
        resp = client.get("/divinations/div-1/result")
    assert resp.status_code == 200
    data = resp.json()
    assert data["base_hexagram"] == 1
    assert data["changed_hexagram"] == 2


def test_get_result_no_changing_lines(client):
    with patch("app.api.divinations.divination_service.get_result") as mock:
        mock.return_value = {
            "divination_id": "div-2",
            "question": "测试",
            "category": "其他",
            "timeframe": None,
            "base_hexagram": 1,
            "changed_hexagram": 1,
            "changing_lines": [],
            "lines": [],
            "base_hexagram_data": {"hexagram_id": 1, "name": "乾"},
            "changed_hexagram_data": None,
        }
        resp = client.get("/divinations/div-2/result")
    assert resp.status_code == 200
    assert resp.json()["changing_lines"] == []
    assert resp.json()["changed_hexagram_data"] is None


def test_get_result_not_found(client):
    from fastapi import HTTPException
    with patch("app.api.divinations.divination_service.get_result",
               side_effect=HTTPException(status_code=404, detail="Not found")):
        resp = client.get("/divinations/bad-id/result")
    assert resp.status_code == 404
