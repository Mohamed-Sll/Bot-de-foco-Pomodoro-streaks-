"""handlers/callbacks.py — Router de callbacks dos botões inline."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from constants import CALLBACK_NEW_FOCUS, CALLBACK_NEW_BREAK, CALLBACK_CANCEL_SESSION
from database import users as users_db
from services.db_async import run_in_thread
from services.session_service import SessionError, cancel_active_session, start_break_session, start_focus_session
from utils.formatting import session_cancelled_message, session_started_message
from utils.keyboards import active_session_keyboard


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    handlers = {
        CALLBACK_NEW_FOCUS: _handle_new_focus,
        CALLBACK_NEW_BREAK: _handle_new_break,
        CALLBACK_CANCEL_SESSION: _handle_cancel,
    }

    handler = handlers.get(query.data)
    if handler is None:
        await query.edit_message_text("Ação desconhecida.")
        return

    await handler(query, user)


async def _handle_new_focus(query, user: dict) -> None:
    try:
        session = await start_focus_session(user["id"])
    except SessionError as exc:
        await query.edit_message_text(f"⚠️ {exc}")
        return

    await query.edit_message_text(
        session_started_message(session["planned_duration_min"]),
        reply_markup=active_session_keyboard(),
    )


async def _handle_new_break(query, user: dict) -> None:
    try:
        session = await start_break_session(user["id"])
    except SessionError as exc:
        await query.edit_message_text(f"⚠️ {exc}")
        return

    await query.edit_message_text(
        session_started_message(session["planned_duration_min"]),
        reply_markup=active_session_keyboard(),
    )


async def _handle_cancel(query, user: dict) -> None:
    cancelled = await cancel_active_session(user["id"])

    if not cancelled:
        await query.edit_message_text("Não tens nenhuma sessão ativa.")
        return

    await query.edit_message_text(session_cancelled_message())