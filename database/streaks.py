

from __future__ import annotations

from datetime import date, timedelta
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


def _parse_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def get_streak(user_id: int) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM streaks WHERE user_id = {_ph()}", (user_id,)
        )
        row = cursor.fetchone()

        if row is None:
            cursor.execute(
                f"""
                INSERT INTO streaks (user_id, current_streak, longest_streak, last_active_date)
                VALUES ({_ph()}, 0, 0, NULL)
                """,
                (user_id,),
            )
            cursor.execute(
                f"SELECT * FROM streaks WHERE user_id = {_ph()}", (user_id,)
            )
            row = cursor.fetchone()

        result = dict(row)
        result["last_active_date"] = _parse_date(result["last_active_date"])
        return result


def record_activity(user_id: int, activity_date: date, minutes: int) -> dict:
    raise NotImplementedError(
        "Ver streak_service.py — record_activity foi dividida em "
        "upsert_daily_stats() e save_streak() abaixo, para separar "
        "'calcular o streak' de 'gravar o streak'."
    )


def upsert_daily_stats(user_id: int, activity_date: date, minutes: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO daily_stats (user_id, date, total_minutes, sessions_count)
            VALUES ({_ph()}, {_ph()}, {_ph()}, 1)
            ON CONFLICT (user_id, date) DO UPDATE SET
                total_minutes = daily_stats.total_minutes + {_ph()},
                sessions_count = daily_stats.sessions_count + 1
            """,
            (user_id, activity_date.isoformat(), minutes, minutes),
        )


def save_streak(user_id: int, current_streak: int, longest_streak: int, last_active_date: date) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO streaks (user_id, current_streak, longest_streak, last_active_date)
            VALUES ({_ph()}, {_ph()}, {_ph()}, {_ph()})
            ON CONFLICT (user_id) DO UPDATE SET
                current_streak = {_ph()},
                longest_streak = {_ph()},
                last_active_date = {_ph()}
            """,
            (
                user_id, current_streak, longest_streak, last_active_date.isoformat(),
                current_streak, longest_streak, last_active_date.isoformat(),
            ),
        )
        cursor.execute(f"SELECT * FROM streaks WHERE user_id = {_ph()}", (user_id,))
        row = dict(cursor.fetchone())
        row["last_active_date"] = _parse_date(row["last_active_date"])
        return row


def get_daily_stats_since(user_id: int, since_date: date) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM daily_stats
            WHERE user_id = {_ph()} AND date >= {_ph()}
            ORDER BY date ASC
            """,
            (user_id, since_date.isoformat()),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    for row in rows:
        row["date"] = _parse_date(row["date"])
    return rows