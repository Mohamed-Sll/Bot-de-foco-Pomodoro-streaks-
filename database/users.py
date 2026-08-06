

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse

from config import settings
from database.connection import get_connection


def _get_engine() -> str:
    parsed = urlparse(settings.database_url)
    return "sqlite" if parsed.scheme.startswith("sqlite") else "postgresql"


_ENGINE = _get_engine()


def _ph() -> str:

    return "?" if _ENGINE == "sqlite" else "%s"


def get_or_create_user(telegram_id: int, username: Optional[str] = None) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1º: tentamos encontrar o user pelo telegram_id
        cursor.execute(
            f"SELECT * FROM users WHERE telegram_id = {_ph()}",
            (telegram_id,),
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        if _ENGINE == "postgresql":
            cursor.execute(
                f"INSERT INTO users (telegram_id, username) "
                f"VALUES ({_ph()}, {_ph()}) RETURNING *",
                (telegram_id, username),
            )
            return dict(cursor.fetchone())
        else:
            cursor.execute(
                f"INSERT INTO users (telegram_id, username) VALUES ({_ph()}, {_ph()})",
                (telegram_id, username),
            )
            new_id = cursor.lastrowid
            cursor.execute(f"SELECT * FROM users WHERE id = {_ph()}", (new_id,))
            return dict(cursor.fetchone())


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Usado quando já temos o id interno (ex: vindo de uma focus_session)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {_ph()}", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_timezone(user_id: int, timezone: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE users SET timezone = {_ph()} WHERE id = {_ph()}",
            (timezone, user_id),
        )