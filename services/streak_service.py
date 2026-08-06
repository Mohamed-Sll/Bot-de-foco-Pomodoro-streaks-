"""services/streak_service.py — Lógica de negócio para streaks e stats diárias."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from constants import MIN_MINUTES_TO_COUNT_FOR_STREAK
from database import streaks as streaks_db
from database import users as users_db
from services.db_async import run_in_thread
from utils.time_helpers import user_today


def compute_new_streak(
    last_active_date: Optional[date],
    current_streak: int,
    longest_streak: int,
    today: date,
) -> tuple[int, int]:
    """
    Função pura — decide os novos valores de streak, sem tocar em BD.
    Testável isoladamente (ver tests/test_streak_service.py).
    """
    if last_active_date is None:
        new_current = 1
    elif last_active_date == today:
        new_current = current_streak  # já contou hoje, sem alteração
    elif last_active_date == today - timedelta(days=1):
        new_current = current_streak + 1
    else:
        new_current = 1  # houve um gap, reinicia

    new_longest = max(longest_streak, new_current)
    return new_current, new_longest


async def record_focus_completion(user_id: int, minutes: int) -> dict:
    """
    Chamado pelo sweep_service.py quando uma sessão de foco é concluída.
    Atualiza sempre daily_stats; só atualiza o streak se a duração
    atingir MIN_MINUTES_TO_COUNT_FOR_STREAK.
    """
    user = await run_in_thread(users_db.get_user_by_id, user_id)
    today = user_today(user["timezone"])

    await run_in_thread(streaks_db.upsert_daily_stats, user_id, today, minutes)

    if minutes < MIN_MINUTES_TO_COUNT_FOR_STREAK:
        return await run_in_thread(streaks_db.get_streak, user_id)

    current = await run_in_thread(streaks_db.get_streak, user_id)
    new_current, new_longest = compute_new_streak(
        current["last_active_date"], current["current_streak"], current["longest_streak"], today
    )
    return await run_in_thread(
        streaks_db.save_streak, user_id, new_current, new_longest, today
    )


async def get_streak(user_id: int) -> dict:
    return await run_in_thread(streaks_db.get_streak, user_id)


async def get_weekly_stats(user_id: int) -> dict:
    since = date.today() - timedelta(days=7)
    daily = await run_in_thread(streaks_db.get_daily_stats_since, user_id, since)
    total_minutes = sum(d["total_minutes"] for d in daily)
    sessions_count = sum(d["sessions_count"] for d in daily)
    return {"total_minutes": total_minutes, "sessions_count": sessions_count, "days": daily} 