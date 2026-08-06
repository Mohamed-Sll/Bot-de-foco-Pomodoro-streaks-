"""utils/keyboards.py — Inline keyboards do bot."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from constants import CALLBACK_NEW_FOCUS, CALLBACK_NEW_BREAK, CALLBACK_CANCEL_SESSION


def active_session_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancelar", callback_data=CALLBACK_CANCEL_SESSION)]
    ])


def session_completed_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Novo foco", callback_data=CALLBACK_NEW_FOCUS),
            InlineKeyboardButton("☕ Pausa", callback_data=CALLBACK_NEW_BREAK),
        ]
    ])