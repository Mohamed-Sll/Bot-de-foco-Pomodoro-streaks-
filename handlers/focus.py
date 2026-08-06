"""handlers/focus.py — Comandos /foco e /cancelar."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import users as users_db
from services.db_async import run_in_thread
from services.session_service import SessionError, cancel_active_session, start_focus_session
from utils.formatting import session_cancelled_message, session_started_message
from utils.keyboards import active_session_keyboard


def _parse_args(args: list[str]) -> tuple[int | None, str | None]:
    """'/foco 30 estudo' -> (30, 'estudo'); '/foco estudo' -> (None, 'estudo')."""
    if not args:
        return None, None

    if args[0].isdigit():
        minutes = int(args[0])
        tag = " ".join(args[1:]) or None
        return minutes, tag

    return None, " ".join(args)


async def focus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    minutes, tag = _parse_args(context.args)

    try:
        session = await start_focus_session(user["id"], minutes, tag)
    except SessionError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return

    await update.message.reply_text(
        session_started_message(session["planned_duration_min"]),
        reply_markup=active_session_keyboard(),
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    cancelled = await cancel_active_session(user["id"])

    if not cancelled:
        await update.message.reply_text("Não tens nenhuma sessão ativa.")
        return

    await update.message.reply_text(session_cancelled_message())