"""handlers/stats.py — Comandos /stats, /streak, /historico."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import users as users_db
from services.db_async import run_in_thread
from services.session_service import get_recent_sessions
from services.streak_service import get_streak, get_weekly_stats
from utils.formatting import history_line, stats_summary_message, streak_message


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    weekly = await get_weekly_stats(user["id"])
    streak = await get_streak(user["id"])

    await update.message.reply_text(
        stats_summary_message(
            weekly["total_minutes"], weekly["sessions_count"], streak["current_streak"]
        ),
        parse_mode="Markdown",
    )


async def streak_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    streak = await get_streak(user["id"])
    await update.message.reply_text(
        f"{streak_message(streak['current_streak'])}\n"
        f"🏆 Recorde: {streak['longest_streak']} dias"
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = update.effective_user
    user = await run_in_thread(users_db.get_or_create_user, telegram_user.id, telegram_user.username)

    recent = await get_recent_sessions(user["id"], limit=10)

    if not recent:
        await update.message.reply_text("Ainda não tens sessões registadas.")
        return

    lines = [
        history_line(s["started_at"], s["planned_duration_min"], s["tag"], s["status"])
        for s in recent
    ]
    await update.message.reply_text("📜 Últimas sessões:\n\n" + "\n".join(lines))