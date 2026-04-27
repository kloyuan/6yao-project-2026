import os
import pytest
from unittest.mock import MagicMock

# Set env vars before any app import
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-anthropic")
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-test-deepseek")

from fastapi.testclient import TestClient
from app.main import app
from app.db import get_supabase


def make_mock_db():
    """Return a MagicMock that simulates the Supabase chained query API."""
    m = MagicMock()
    # Every chained attribute/call returns the same mock so callers can set
    # .execute.return_value or .execute.side_effect freely.
    for attr in ("table", "select", "insert", "update", "eq", "order", "execute"):
        getattr(m, attr).return_value = m
    return m


@pytest.fixture
def mock_db():
    return make_mock_db()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_supabase] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
