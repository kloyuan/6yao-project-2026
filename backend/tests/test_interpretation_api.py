from unittest.mock import patch
from fastapi import HTTPException


def test_interpret_success_returns_all_fields(client):
    with patch(
        "app.api.interpretations.interpretation_service.get_or_create_interpretation"
    ) as mock:
        mock.return_value = {
            "divination_id": "div-1",
            "summary": "总体形势良好",
            "base_reading": "本卦乾象征刚健",
            "changing_lines_analysis": "第一爻动爻...",
            "changed_hexagram_trend": "变为坤卦...",
            "category_advice": "事业上宜积极进取",
            "action_advice": ["建议一", "建议二", "建议三"],
            "generated_by": "ai",
            "provider": "claude",
        }
        resp = client.post("/divinations/div-1/interpret")

    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "总体形势良好"
    assert data["base_reading"] is not None
    assert data["changing_lines_analysis"] is not None
    assert data["changed_hexagram_trend"] is not None
    assert data["category_advice"] is not None
    assert len(data["action_advice"]) == 3
    assert data["error"] is None


def test_interpret_llm_failure_returns_readable_error(client):
    with patch(
        "app.api.interpretations.interpretation_service.get_or_create_interpretation"
    ) as mock:
        mock.return_value = {
            "divination_id": "div-1",
            "error": "AI 解读暂时不可用，请稍后再试。卦象盘面不受影响，可继续查看。",
            "generated_by": "ai",
        }
        resp = client.post("/divinations/div-1/interpret")

    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is not None
    assert "AI" in data["error"]


def test_interpret_repeat_call_returns_existing(client):
    """Repeated calls should not generate a new interpretation."""
    cached = {
        "divination_id": "div-1",
        "summary": "已有解读",
        "base_reading": "本卦...",
        "changing_lines_analysis": "",
        "changed_hexagram_trend": "",
        "category_advice": "...",
        "action_advice": ["a", "b", "c"],
        "generated_by": "ai",
        "provider": "claude",
    }
    with patch(
        "app.api.interpretations.interpretation_service.get_or_create_interpretation",
        return_value=cached,
    ) as mock:
        client.post("/divinations/div-1/interpret")
        resp = client.post("/divinations/div-1/interpret")
        assert mock.call_count == 2  # called twice but service decides to reuse

    assert resp.json()["summary"] == "已有解读"


def test_interpret_not_found(client):
    with patch(
        "app.api.interpretations.interpretation_service.get_or_create_interpretation",
        side_effect=HTTPException(status_code=404, detail="Not found"),
    ):
        resp = client.post("/divinations/bad-id/interpret")
    assert resp.status_code == 404
