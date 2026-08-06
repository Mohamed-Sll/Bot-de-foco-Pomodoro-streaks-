"""utils/formatting.py — Mensagens de texto formatadas para o Telegram."""

from __future__ import annotations

from constants import (
    MSG_SESSION_STARTED,
    MSG_SESSION_COMPLETED,
    MSG_SESSION_CANCELLED,
    MSG_STREAK_UPDATE,
)
from utils.time_helpers import format_duration


def session_started_message(minutes: int) -> str:
    return MSG_SESSION_STARTED.format(minutes=minutes)


def session_completed_message(minutes: int) -> str:
    return MSG_SESSION_COMPLETED.format(minutes=minutes)


def session_cancelled_message() -> str:
    return MSG_SESSION_CANCELLED


def streak_message(days: int) -> str:
    return MSG_STREAK_UPDATE.format(days=days)


def stats_summary_message(total_minutes: int, sessions_count: int, streak_days: int) -> str:
    return (
        f"📊 *Resumo*\n\n"
        f"Tempo focado: {format_duration(total_minutes)}\n"
        f"Sessões: {sessions_count}\n"
        f"🔥 Streak: {streak_days} dias"
    )


def history_line(started_at, duration_min: int, tag: str | None, status: str) -> str:
    date_str = started_at.strftime("%d/%m %H:%M")
    tag_str = f" · {tag}" if tag else ""
    icon = "✅" if status == "completed" else "❌"
    return f"{icon} {date_str} — {format_duration(duration_min)}{tag_str}"