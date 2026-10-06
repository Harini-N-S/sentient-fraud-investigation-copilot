"""
Rawbank Sentient Fraud Intelligence Platform
Database Connection and Session Management
-----------------------------------------------------------------------------
Provides SQLite connection factory, row-mapping utilities, and connectivity checks.
Enforces foreign key integrity on all connections.
"""

import sqlite3
from typing import Generator
from pathlib import Path
from backend.app.config import settings


def get_db_path() -> Path:
    """Return configured database path."""
    return settings.database_path


def create_connection(db_path: Path = None) -> sqlite3.Connection:
    """
    Create a new SQLite connection with row factory and foreign keys enabled.
    """
    path = db_path or get_db_path()
    if not path.exists():
        raise FileNotFoundError(f"Database file not found at: {path}")

    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency that yields a database connection and closes it on completion.
    """
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()


def check_db_connectivity() -> dict:
    """
    Tests actual database connectivity by executing a lightweight query and checking table presence.
    Returns status dictionary.
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
        table_count = cursor.fetchone()[0]
        conn.close()

        if result and result[0] == 1 and table_count > 0:
            return {"status": "connected", "table_count": table_count, "error": None}
        else:
            return {"status": "disconnected", "table_count": 0, "error": "Unexpected query response"}
    except Exception as e:
        return {"status": "error", "table_count": 0, "error": str(e)}
