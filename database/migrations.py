from __future__ import annotations
from urllib.parse import urlparse
from config import settings
from database.connection import get_connection

# --- Deteção do motor (repetida aqui de propósito) -----------------------
def _get_engine() -> str:
    parsed = urlparse(settings.database_url)
    return "sqlite" if parsed.scheme.startswith("sqlite") else "postgresql"


_ENGINE = _get_engine()


def _pk() -> str:
    if _ENGINE == "sqlite":
        return "INTEGER PRIMARY KEY AUTOINCREMENT"
    return "SERIAL PRIMARY KEY"


# --- Definição de cada tabela, como uma lista de statements SQL -----------
def _table_statements() -> list[str]:
    return [

        f"""
        CREATE TABLE IF NOT EXISTS users (
            id {_pk()},
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            timezone TEXT NOT NULL DEFAULT 'Atlantic/Cape_Verde',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        f"""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id {_pk()},
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type TEXT NOT NULL DEFAULT 'focus',
            planned_duration_min INTEGER NOT NULL,
            actual_duration_min INTEGER,
            status TEXT NOT NULL DEFAULT 'active',
            tag TEXT,
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        )
        """,

        f"""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            current_streak INTEGER NOT NULL DEFAULT 0,
            longest_streak INTEGER NOT NULL DEFAULT 0,
            last_active_date DATE
        )
        """,

        f"""
        CREATE TABLE IF NOT EXISTS daily_stats (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            total_minutes INTEGER NOT NULL DEFAULT 0,
            sessions_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, date)
        )
        """,
    ]


# --- Índices ---------------------------------------------------------------
def _index_statements() -> list[str]:
    return [
        "CREATE INDEX IF NOT EXISTS idx_sessions_status ON focus_sessions(status)",
        "CREATE INDEX IF NOT EXISTS idx_sessions_user ON focus_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)",
    ]


def run_migrations() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        for statement in _table_statements():
            cursor.execute(statement)

        for statement in _index_statements():
            cursor.execute(statement)

