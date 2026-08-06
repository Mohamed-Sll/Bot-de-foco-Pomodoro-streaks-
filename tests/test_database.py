# tests/test_database.py
"""CRUD básico de users e sessions."""

from database import sessions as sessions_db
from database import users as users_db


def test_get_or_create_user_creates_once(create_user):
    user1 = create_user(telegram_id=100)
    user2 = users_db.get_or_create_user(telegram_id=100)
    assert user1["id"] == user2["id"]


def test_update_timezone(create_user):
    user = create_user(telegram_id=101)
    users_db.update_timezone(user["id"], "Europe/Lisbon")
    updated = users_db.get_user_by_id(user["id"])
    assert updated["timezone"] == "Europe/Lisbon"


def test_create_and_get_active_session(create_user):
    user = create_user(telegram_id=102)
    session = sessions_db.create_session(user["id"], "focus", 25, tag="estudo")

    active = sessions_db.get_active_session(user["id"])
    assert active["id"] == session["id"]
    assert active["status"] == "active"


def test_complete_session_removes_it_from_active(create_user):
    user = create_user(telegram_id=103)
    session = sessions_db.create_session(user["id"], "focus", 25)

    sessions_db.complete_session(session["id"], actual_duration_min=25)

    assert sessions_db.get_active_session(user["id"]) is None


def test_cancel_session(create_user):
    user = create_user(telegram_id=104)
    session = sessions_db.create_session(user["id"], "focus", 25)

    sessions_db.cancel_session(session["id"])

    recent = sessions_db.get_recent_sessions(user["id"])
    assert recent[0]["status"] == "cancelled"