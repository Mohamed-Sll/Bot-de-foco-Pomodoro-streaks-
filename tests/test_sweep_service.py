# tests/test_sweep_service.py
"""Deteção de sessões prontas e idempotência do sweep job."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from services.session_service import get_active_session, start_focus_session
from services.sweep_service import run_sweep_once


def _rewind_started_at(session_id: int, minutes_ago: int = 26) -> None:
    from database.connection import get_connection

    past = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE focus_sessions SET started_at = ? WHERE id = ?",
            (past.isoformat(), session_id),
        )


@pytest.mark.asyncio
async def test_sweep_completes_due_session(create_user):
    user = create_user(telegram_id=400)
    session = await start_focus_session(user["id"], minutes=25)
    _rewind_started_at(session["id"])

    fake_bot = AsyncMock()
    processed = await run_sweep_once(fake_bot)

    assert processed == 1
    assert await get_active_session(user["id"]) is None
    fake_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_sweep_ignores_session_not_yet_due(create_user):
    user = create_user(telegram_id=401)
    await start_focus_session(user["id"], minutes=25)

    fake_bot = AsyncMock()
    processed = await run_sweep_once(fake_bot)

    assert processed == 0
    fake_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_sweep_does_not_reprocess_completed_session(create_user):
    user = create_user(telegram_id=402)
    session = await start_focus_session(user["id"], minutes=25)
    _rewind_started_at(session["id"])

    fake_bot = AsyncMock()
    await run_sweep_once(fake_bot)
    processed_again = await run_sweep_once(fake_bot)

    assert processed_again == 0
    assert fake_bot.send_message.call_count == 1