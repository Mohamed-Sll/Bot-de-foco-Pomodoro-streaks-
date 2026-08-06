"""handlers/settings.py — Comando /timezone."""

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from telegram import Update
from telegram.ext import ContextTypes

from database import users as users_db
from services.db_async import run_in_thread


async def timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    if not context.args:
        await update.message.reply_text(
            f"Timezone atual: {user['timezone']}\n\n"
            "Usa /timezone [zona], ex: /timezone Europe/Lisbon"
        )
        return

    tz_name = context.args[0]

    try:
        ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        await update.message.reply_text(
            f"⚠️ Timezone inválida: {tz_name}\n"
            "Ex: Atlantic/Cape_Verde, Europe/Lisbon"
        )
        return

    await run_in_thread(users_db.update_timezone, user["id"], tz_name)
    await update.message.reply_text(f"✅ Timezone atualizada para {tz_name}")