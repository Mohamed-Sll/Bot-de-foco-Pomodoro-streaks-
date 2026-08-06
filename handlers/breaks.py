"""handlers/breaks.py — Comando /pausa."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import users as users_db
from services.db_async import run_in_thread
from services.session_service import SessionError, start_break_session
from utils.formatting import session_started_message
from utils.keyboards import active_session_keyboard


async def break_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    minutes = None
    if context.args and context.args[0].isdigit():
        minutes = int(context.args[0])

    try:
        session = await start_break_session(user["id"], minutes)
    except SessionError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return

    await update.message.reply_text(
        session_started_message(session["planned_duration_min"]),
        reply_markup=active_session_keyboard(),
    )