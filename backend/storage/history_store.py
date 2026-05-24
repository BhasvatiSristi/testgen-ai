"""SQLite-backed history store for generated test runs."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "testgen_history.db"


def _get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_db() -> None:
    with _get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                input_type TEXT NOT NULL,
                framework TEXT NOT NULL,
                input_summary TEXT NOT NULL,
                unit_tests TEXT NOT NULL,
                integration_tests TEXT NOT NULL,
                edge_cases TEXT NOT NULL,
                coverage_pct INTEGER NOT NULL
            )
            """
        )
        connection.commit()


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def save_run(run: dict) -> int:
    """Persist a generation run and return the inserted row id."""

    _initialize_db()
    timestamp = run.get("timestamp") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO runs (
                timestamp,
                input_type,
                framework,
                input_summary,
                unit_tests,
                integration_tests,
                edge_cases,
                coverage_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                str(run.get("input_type", "")),
                str(run.get("framework", "")),
                str(run.get("input_summary", "")),
                str(run.get("unit_tests", "")),
                str(run.get("integration_tests", "")),
                str(run.get("edge_cases", "")),
                int(run.get("coverage_pct", 0) or 0),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_all_runs() -> list[dict]:
    """Return the most recent 20 runs, newest first."""

    _initialize_db()
    with _get_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT 20"
        )
        return [_row_to_dict(row) for row in cursor.fetchall()]


def get_run_by_id(run_id: int) -> dict:
    """Return a single run by its primary key."""

    _initialize_db()
    with _get_connection() as connection:
        cursor = connection.execute("SELECT * FROM runs WHERE id = ?", (int(run_id),))
        row = cursor.fetchone()
        return _row_to_dict(row) if row else {}


def delete_run(run_id: int) -> None:
    """Delete a run from the history store."""

    _initialize_db()
    with _get_connection() as connection:
        connection.execute("DELETE FROM runs WHERE id = ?", (int(run_id),))
        connection.commit()


_initialize_db()