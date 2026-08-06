# tests/test_streak_service.py
"""Lógica de streak: gaps, mesmo dia, sequência, recorde."""

from datetime import date, timedelta

import pytest

from services.streak_service import compute_new_streak, record_focus_completion


def test_first_ever_activity_starts_streak_at_one():
    current, longest = compute_new_streak(None, 0, 0, date(2026, 8, 6))
    assert current == 1
    assert longest == 1


def test_same_day_does_not_increment():
    today = date(2026, 8, 6)
    current, longest = compute_new_streak(today, 3, 3, today)
    assert current == 3


def test_consecutive_day_increments():
    today = date(2026, 8, 6)
    yesterday = today - timedelta(days=1)
    current, longest = compute_new_streak(yesterday, 3, 5, today)
    assert current == 4
    assert longest == 5


def test_gap_resets_streak_but_keeps_record():
    today = date(2026, 8, 6)
    three_days_ago = today - timedelta(days=3)
    current, longest = compute_new_streak(three_days_ago, 10, 10, today)
    assert current == 1
    assert longest == 10


def test_new_streak_beats_record():
    today = date(2026, 8, 6)
    yesterday = today - timedelta(days=1)
    current, longest = compute_new_streak(yesterday, 5, 5, today)
    assert current == 6
    assert longest == 6


@pytest.mark.asyncio
async def test_below_minimum_minutes_does_not_update_streak(create_user):
    user = create_user(telegram_id=300)
    result = await record_focus_completion(user["id"], minutes=3)
    assert result["current_streak"] == 0