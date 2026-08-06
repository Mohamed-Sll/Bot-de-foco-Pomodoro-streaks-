"""time_helpers.py — Conversões de timezone e cálculo de "dia" por user."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from zoneinfo import ZoneInfo


def to_user_timezone(dt_utc: datetime, timezone: str) -> datetime:
    """Converte um datetime em UTC para a timezone do user."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
    return dt_utc.astimezone(ZoneInfo(timezone))


def user_today(timezone: str) -> date:
    """Devolve a data de "hoje" segundo a timezone do user."""
    return datetime.now(ZoneInfo(timezone)).date()


def is_yesterday(reference_date: date, timezone: str) -> bool:
    return reference_date == user_today(timezone) - timedelta(days=1)


def is_today(reference_date: date, timezone: str) -> bool:
    return reference_date == user_today(timezone)


def format_duration(minutes: int) -> str:
    """Ex: 90 -> '1h30', 25 -> '25min'."""
    if minutes < 60:
        return f"{minutes}min"
    hours, rest = divmod(minutes, 60)
    return f"{hours}h{rest:02d}" if rest else f"{hours}h"