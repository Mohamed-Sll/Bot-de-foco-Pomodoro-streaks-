from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator, Union
from urllib.parse import urlparse

from config import settings

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2 import pool as pg_pool
except ImportError:
    psycopg2 = None
    pg_pool = None


# --- Deteção do motor a partir da DATABASE_URL --------------------------------
def _get_engine() -> str:
    parsed = urlparse(settings.database_url)
    if parsed.scheme.startswith("sqlite"):
        return "sqlite"
    if parsed.scheme.startswith("postgres"):
        return "postgresql"
    raise ValueError(f"DATABASE_URL com esquema não suportado: {parsed.scheme}")


_ENGINE = _get_engine()
_pg_connection_pool: "pg_pool.ThreadedConnectionPool | None" = None


def _init_postgres_pool() -> None:
    global _pg_connection_pool
    if _pg_connection_pool is not None:
        return
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 não está instalado, mas DATABASE_URL aponta para PostgreSQL. "
            "Corre: pip install psycopg2-binary"
        )
    _pg_connection_pool = pg_pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,  
        dsn=settings.database_url,
    )


# --- SQLite: extrair o path do ficheiro a partir da URL -----------------------
def _sqlite_path() -> str:
    return settings.database_url.replace("sqlite:///", "").replace("sqlite://", "")


def _create_sqlite_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_sqlite_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_connection() -> Iterator[Union[sqlite3.Connection, "psycopg2.extensions.connection"]]:
    if _ENGINE == "sqlite":
        conn = _create_sqlite_connection()
        try:
            yield conn
            conn.commit()         
        except Exception:
            conn.rollback()        
            raise
        finally:
            conn.close()

    else:  # postgresql
        _init_postgres_pool()
        conn = _pg_connection_pool.getconn()
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _pg_connection_pool.putconn(conn)  


# --- Fecho limpo no shutdown do bot --------------------------------------------
def close_all_connections() -> None:
    if _pg_connection_pool is not None:
        _pg_connection_pool.closeall()