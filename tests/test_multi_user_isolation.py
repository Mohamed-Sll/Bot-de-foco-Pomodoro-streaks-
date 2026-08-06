# tests/test_multi_user_isolation.py
"""Sessão/streak do user A não vaza para o user B."""

import pytest

from services.session_service import get_active_session, start_focus_session
from services.streak_service import get_streak, record_focus_completion


@pytest.mark.asyncio
async def test_active_session_isolated_between_users(create_user):
    user_a = create_user(telegram_id=500)
    user_b = create_user(telegram_id=501)

    await start_focus_session(user_a["id"], minutes=25)

    assert await get_active_session(user_a["id"]) is not None
    assert await get_active_session(user_b["id"]) is None


@pytest.mark.asyncio
async def test_streak_isolated_between_users(create_user):
    user_a = create_user(telegram_id=502)
    user_b = create_user(telegram_id=503)

    await record_focus_completion(user_a["id"], minutes=20)

    streak_a = await get_streak(user_a["id"])
    streak_b = await get_streak(user_b["id"])

    assert streak_a["current_streak"] == 1
    assert streak_b["current_streak"] == 0


@pytest.mark.asyncio
async def test_second_user_unaffected_by_first_users_active_session(create_user):
    user_a = create_user(telegram_id=504)
    user_b = create_user(telegram_id=505)

    await start_focus_session(user_a["id"])
    session_b = await start_focus_session(user_b["id"])

    assert session_b is not None