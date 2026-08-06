# tests/test_session_service.py
"""Regras de negócio de sessões (duração, sessão única ativa)."""

import pytest

from services.session_service import (
    SessionError,
    cancel_active_session,
    start_break_session,
    start_focus_session,
)


@pytest.mark.asyncio
async def test_start_focus_session_default_duration(create_user):
    user = create_user(telegram_id=200)
    session = await start_focus_session(user["id"])
    assert session["planned_duration_min"] == 25
    assert session["type"] == "focus"


@pytest.mark.asyncio
async def test_start_focus_session_rejects_duration_out_of_range(create_user):
    user = create_user(telegram_id=201)
    with pytest.raises(SessionError):
        await start_focus_session(user["id"], minutes=999)


@pytest.mark.asyncio
async def test_cannot_start_two_sessions_at_once(create_user):
    user = create_user(telegram_id=202)
    await start_focus_session(user["id"])

    with pytest.raises(SessionError):
        await start_focus_session(user["id"])


@pytest.mark.asyncio
async def test_cancel_then_start_new_session(create_user):
    user = create_user(telegram_id=203)
    await start_focus_session(user["id"])

    cancelled = await cancel_active_session(user["id"])
    assert cancelled is not None

    session = await start_break_session(user["id"])
    assert session["type"] == "break"