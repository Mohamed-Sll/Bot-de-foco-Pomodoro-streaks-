# tests/conftest.py
"""Fixtures partilhadas: BD temporária e limpeza entre testes."""

import os
import tempfile

import pytest

# DATABASE_URL tem de estar definida ANTES de qualquer import do projeto,
# porque config.py lê as env vars no momento do import.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("WEBHOOK_URL", "https://example.com")
os.environ.setdefault("WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db_path}")
os.environ.setdefault("ENVIRONMENT", "test")

from database.connection import get_connection  # noqa: E402
from database.migrations import run_migrations  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    run_migrations()
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        for table in ("daily_stats", "streaks", "focus_sessions", "users"):
            cursor.execute(f"DELETE FROM {table}")


@pytest.fixture
def create_user():
    from database import users as users_db

    def _create(telegram_id: int = 111, username: str = "testuser"):
        return users_db.get_or_create_user(telegram_id, username)

    return _create