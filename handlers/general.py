"""handlers/general.py — Comandos básicos: /start, /ajuda, /comandos."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import users as users_db
from services.db_async import run_in_thread

COMMANDS_TEXT = (
    "🎯 /foco [minutos] [tag] — inicia uma sessão de foco (default 25 min)\n"
    "☕ /pausa [minutos] — inicia uma pausa (default 5 min)\n"
    "❌ /cancelar — cancela a sessão ativa\n"
    "📊 /stats — resumo da semana\n"
    "🔥 /streak — streak atual\n"
    "📜 /historico — últimas sessões\n"
    "⚙️ /timezone [zona] — muda a tua timezone\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await run_in_thread(users_db.get_or_create_user, user.id, user.username)

    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n\n"
        "Sou o teu bot de foco. Usa /foco para começares uma sessão.\n\n"
        f"{COMMANDS_TEXT}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(COMMANDS_TEXT)


async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(COMMANDS_TEXT)