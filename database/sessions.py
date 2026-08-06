

from __future__ import annotations

from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from config import settings
from constants import SESSION_ACTIVE, SESSION_COMPLETED, SESSION_CANCELLED
from database.connection import get_connection


def _get_engine() -> str:
    parsed = urlparse(settings.database_url)
    return "sqlite" if parsed.scheme.startswith("sqlite") else "postgresql"


_ENGINE = _get_engine()


def _ph() -> str:
    return "?" if _ENGINE == "sqlite" else "%s"


def _parse_timestamp(value) -> datetime:

    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def create_session(
    user_id: int,
    session_type: str,
    planned_duration_min: int,
    tag: Optional[str] = None,
) -> dict:
    
    with get_connection() as conn:
        cursor = conn.cursor()

        if _ENGINE == "postgresql":
            cursor.execute(
                f"""
                INSERT INTO focus_sessions
                    (user_id, type, planned_duration_min, status, tag)
                VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})
                RETURNING *
                """,
                (user_id, session_type, planned_duration_min, SESSION_ACTIVE, tag),
            )
            return dict(cursor.fetchone())
        else:
            cursor.execute(
                f"""
                INSERT INTO focus_sessions
                    (user_id, type, planned_duration_min, status, tag)
                VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()}, {_ph()})
                """,
                (user_id, session_type, planned_duration_min, SESSION_ACTIVE, tag),
            )
            new_id = cursor.lastrowid
            cursor.execute(f"SELECT * FROM focus_sessions WHERE id = {_ph()}", (new_id,))
            return dict(cursor.fetchone())


def get_active_session(user_id: int) -> Optional[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM focus_sessions
            WHERE user_id = {_ph()} AND status = {_ph()}
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (user_id, SESSION_ACTIVE),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_active_sessions() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM focus_sessions WHERE status = {_ph()}",
            (SESSION_ACTIVE,),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    for row in rows:
        row["started_at"] = _parse_timestamp(row["started_at"])

    return rows


def complete_session(session_id: int, actual_duration_min: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE focus_sessions
            SET status = {_ph()}, actual_duration_min = {_ph()},
                ended_at = CURRENT_TIMESTAMP
            WHERE id = {_ph()}
            """,
            (SESSION_COMPLETED, actual_duration_min, session_id),
        )


def cancel_session(session_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE focus_sessions
            SET status = {_ph()}, ended_at = CURRENT_TIMESTAMP
            WHERE id = {_ph()}
            """,
            (SESSION_CANCELLED, session_id),
        )


def get_recent_sessions(user_id: int, limit: int = 10) -> list[dict]:
    """Usado por /historico — as últimas N sessões do user, mais recente primeiro."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM focus_sessions
            WHERE user_id = {_ph()}
            ORDER BY started_at DESC
            LIMIT {_ph()}
            """,
            (user_id, limit),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_sessions_since(user_id: int, since: datetime) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM focus_sessions
            WHERE user_id = {_ph()}
              AND status = {_ph()}
              AND type = 'focus'
              AND started_at >= {_ph()}
            ORDER BY started_at ASC
            """,
            (user_id, SESSION_COMPLETED, since.isoformat()),
        )
        return [dict(row) for row in cursor.fetchall()]