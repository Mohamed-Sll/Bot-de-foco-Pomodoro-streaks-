"""services/session_service.py — Lógica de negócio para sessões de foco e pausa."""

from __future__ import annotations

from typing import Optional

from config import settings
from constants import (
    SESSION_TYPE_FOCUS,
    SESSION_TYPE_BREAK,
    DEFAULT_FOCUS_MINUTES,
    DEFAULT_SHORT_BREAK_MINUTES,
)
from database import sessions as sessions_db
from services.db_async import run_in_thread


class SessionError(Exception):
    """Erro de validação ou de estado ao gerir uma sessão."""


async def start_focus_session(
    user_id: int, minutes: Optional[int] = None, tag: Optional[str] = None
) -> dict:
    minutes = minutes or DEFAULT_FOCUS_MINUTES

    if not (settings.min_focus_minutes <= minutes <= settings.max_focus_minutes):
        raise SessionError(
            f"Duração deve estar entre {settings.min_focus_minutes} "
            f"e {settings.max_focus_minutes} minutos."
        )

    active = await run_in_thread(sessions_db.get_active_session, user_id)
    if active:
        raise SessionError("Já tens uma sessão ativa. Usa /cancelar antes de começar outra.")

    return await run_in_thread(
        sessions_db.create_session, user_id, SESSION_TYPE_FOCUS, minutes, tag
    )


async def start_break_session(user_id: int, minutes: Optional[int] = None) -> dict:
    minutes = minutes or DEFAULT_SHORT_BREAK_MINUTES

    active = await run_in_thread(sessions_db.get_active_session, user_id)
    if active:
        raise SessionError("Já tens uma sessão ativa. Usa /cancelar antes de começar outra.")

    return await run_in_thread(
        sessions_db.create_session, user_id, SESSION_TYPE_BREAK, minutes, None
    )


async def cancel_active_session(user_id: int) -> Optional[dict]:
    active = await run_in_thread(sessions_db.get_active_session, user_id)
    if not active:
        return None

    await run_in_thread(sessions_db.cancel_session, active["id"])
    return active


async def get_active_session(user_id: int) -> Optional[dict]:
    return await run_in_thread(sessions_db.get_active_session, user_id)


async def complete_session(session_id: int, actual_duration_min: int) -> None:
    await run_in_thread(sessions_db.complete_session, session_id, actual_duration_min)


async def get_recent_sessions(user_id: int, limit: int = 10) -> list[dict]:
    return await run_in_thread(sessions_db.get_recent_sessions, user_id, limit)