"""services/sweep_service.py — Job periódico que deteta sessões terminadas e notifica."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from constants import CALLBACK_NEW_FOCUS, CALLBACK_NEW_BREAK, SESSION_TYPE_FOCUS
from database import sessions as sessions_db
from database import users as users_db
from services.db_async import run_in_thread
from services.session_service import complete_session
from services.streak_service import record_focus_completion
from utils.formatting import session_completed_message

logger = logging.getLogger(__name__)


def _is_due(session: dict, now: datetime) -> bool:
    elapsed = (now - session["started_at"]).total_seconds() / 60
    return elapsed >= session["planned_duration_min"]


def _completion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Novo foco", callback_data=CALLBACK_NEW_FOCUS),
            InlineKeyboardButton("☕ Pausa", callback_data=CALLBACK_NEW_BREAK),
        ]
    ])


async def _process_due_session(bot: Bot, session: dict) -> None:
    # Marca completado antes de notificar, para não reprocessar no próximo ciclo se o envio falhar.
    await complete_session(session["id"], session["planned_duration_min"])

    if session["type"] == SESSION_TYPE_FOCUS:
        await record_focus_completion(session["user_id"], session["planned_duration_min"])

    user = await run_in_thread(users_db.get_user_by_id, session["user_id"])
    text = session_completed_message(session["planned_duration_min"])

    try:
        await bot.send_message(
            chat_id=user["telegram_id"], text=text, reply_markup=_completion_keyboard()
        )
    except Exception:
        logger.exception("Falha ao notificar user_id=%s sobre sessão %s", session["user_id"], session["id"])


async def run_sweep_once(bot: Bot) -> int:
    now = datetime.now(timezone.utc)
    active_sessions = await run_in_thread(sessions_db.get_all_active_sessions)
    due = [s for s in active_sessions if _is_due(s, now)]

    for session in due:
        await _process_due_session(bot, session)

    return len(due)


async def start_sweep_loop(bot: Bot) -> None:
    """Loop infinito, arrancado como task no main.py."""
    while True:
        try:
            processed = await run_sweep_once(bot)
            if processed:
                logger.info("Sweep processou %d sessão(ões)", processed)
        except Exception:
            logger.exception("Erro no ciclo do sweep")
        await asyncio.sleep(settings.sweep_interval_seconds)