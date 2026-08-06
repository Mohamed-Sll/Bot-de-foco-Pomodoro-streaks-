"""bot.py — Middleware pipeline e registo de handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
)

from config import settings
from handlers.breaks import break_command
from handlers.callbacks import callback_router
from handlers.focus import cancel_command, focus_command
from handlers.general import commands_command, help_command, start
from handlers.settings import timezone_command
from handlers.stats import history_command, stats_command, streak_command


def build_application() -> Application:
    app = ApplicationBuilder().token(settings.bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", help_command))
    app.add_handler(CommandHandler("comandos", commands_command))

    app.add_handler(CommandHandler("foco", focus_command))
    app.add_handler(CommandHandler("cancelar", cancel_command))
    app.add_handler(CommandHandler("pausa", break_command))

    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("streak", streak_command))
    app.add_handler(CommandHandler("historico", history_command))

    app.add_handler(CommandHandler("timezone", timezone_command))

    app.add_handler(CallbackQueryHandler(callback_router))

    return app