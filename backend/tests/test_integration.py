"""
Integration tests — require a real Supabase database.

Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to a real test project
and run:  pytest backend/tests/test_integration.py -v

Tests are skipped automatically when the placeholder URL is detected.
"""
import os
import pytest

REAL_DB = (
    os.environ.get("SUPABASE_URL", "").startswith("https://")
    and "test.supabase.co" not in os.environ.get("SUPABASE_URL", "")
)

skip_no_db = pytest.mark.skipif(not REAL_DB, reason="requires real Supabase database")


@skip_no_db
def test_full_divination_flow():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Create divination
    resp = client.post("/divinations", json={
        "question": "集成测试问题",
        "category": "其他",
        "session_token": "integration-test-token",
    })
    assert resp.status_code == 200
    div_id = resp.json()["divination_id"]

    # 2. Submit 6 lines (all 少阳 = [3, 2, 2])
    for i in range(1, 7):
        r = client.post(f"/divinations/{div_id}/lines", json={
            "line_number": i,
            "coin_values": [3, 2, 2],
        })
        assert r.status_code == 200
        data = r.json()
        assert data["line_type"] == "少阳"
        assert data["is_changing"] is False

    # 3. Get result — board should be complete
    r = client.get(f"/divinations/{div_id}/result")
    assert r.status_code == 200
    result = r.json()
    assert result["base_hexagram"] is not None
    assert result["changed_hexagram"] == result["base_hexagram"]
    assert result["changing_lines"] == []
    assert len(result["lines"]) == 6


@skip_no_db
def test_no_changing_lines_changed_equals_base():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.post("/divinations", json={
        "question": "无动爻测试",
        "category": "其他",
        "session_token": "integration-test-static",
    })
    div_id = resp.json()["divination_id"]

    for i in range(1, 7):
        client.post(f"/divinations/{div_id}/lines", json={
            "line_number": i,
            "coin_values": [3, 2, 2],  # coin_sum=7 少阳, not changing
        })

    r = client.get(f"/divinations/{div_id}/result")
    data = r.json()
    assert data["changed_hexagram"] == data["base_hexagram"]
    assert data["changing_lines"] == []


@skip_no_db
def test_interpret_returns_full_fields():
    """Requires real LLM API key in addition to Supabase."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.post("/divinations", json={
        "question": "解读测试",
        "category": "事业",
        "session_token": "integration-test-interp",
    })
    div_id = resp.json()["divination_id"]

    for i in range(1, 7):
        client.post(f"/divinations/{div_id}/lines", json={
            "line_number": i,
            "coin_values": [3, 3, 3],  # 老阳, all changing
        })

    r = client.post(f"/divinations/{div_id}/interpret")
    assert r.status_code == 200
    data = r.json()
    if data.get("error"):
        pytest.skip("LLM not available in this environment")
    assert data["summary"]
    assert data["base_reading"]


@skip_no_db
def test_followup_round_limit():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.post("/divinations", json={
        "question": "追问上限测试",
        "category": "其他",
        "session_token": "integration-test-followup",
    })
    div_id = resp.json()["divination_id"]

    for i in range(1, 7):
        client.post(f"/divinations/{div_id}/lines", json={
            "line_number": i,
            "coin_values": [3, 2, 2],
        })

    # Send 20 rounds
    for _ in range(20):
        r = client.post(f"/divinations/{div_id}/followup", json={"message": "追问"})
        if r.status_code == 503:
            pytest.skip("LLM not available")
        assert r.status_code == 200

    # Round 21 must be rejected
    r = client.post(f"/divinations/{div_id}/followup", json={"message": "第21轮"})
    assert r.status_code == 429


@skip_no_db
def test_invalid_id_returns_404():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    assert client.get("/divinations/nonexistent-id/result").status_code == 404
    assert client.post("/divinations/nonexistent-id/interpret").status_code in (404, 422)
    assert client.get("/divinations/nonexistent-id/followup").status_code == 404
