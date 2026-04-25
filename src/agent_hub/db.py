import sqlite3
from datetime import date
from pathlib import Path
from src.agent_hub.ingester import RawItem

CREATE_RAW_ITEMS = """CREATE TABLE IF NOT EXISTS raw_items (
    id           TEXT PRIMARY KEY,
    run_id       TEXT NOT NULL,
    source_name  TEXT NOT NULL,
    title        TEXT NOT NULL,
    link         TEXT NOT NULL,
    published_at TEXT,
    summary      TEXT,
    ingested_at  TEXT NOT NULL
)"""

CREATE_RUNS = """CREATE TABLE IF NOT EXISTS runs (
    run_id         TEXT PRIMARY KEY,
    run_number     INTEGER NOT NULL,
    started_at     TEXT NOT NULL,
    completed_at   TEXT,
    status         TEXT,
    raw_count      INTEGER DEFAULT 0,
    relevant_count INTEGER DEFAULT 0,
    error_message  TEXT
)"""

def init_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite schema if tables do not exist."""
    conn.execute(CREATE_RAW_ITEMS)
    conn.execute(CREATE_RUNS)
    conn.commit()

def next_run_id(conn: sqlite3.Connection) -> tuple[int, str]:
    """Calculate next run number and run ID string."""
    row = conn.execute("SELECT MAX(run_number) FROM runs").fetchone()
    n = (row[0] or 0) + 1
    return n, f"run-{n}-{date.today().isoformat()}"

def start_run(conn: sqlite3.Connection, run_id: str, run_number: int, started_at: str) -> None:
    """Record run start with 'running' status."""
    conn.execute(
        "INSERT INTO runs (run_id, run_number, started_at, status) VALUES (?, ?, ?, ?)",
        (run_id, run_number, started_at, "running")
    )
    conn.commit()

def complete_run(
    conn: sqlite3.Connection,
    run_id: str,
    status: str,
    raw_count: int,
    relevant_count: int,
    completed_at: str,
    error_message: str | None,
) -> None:
    """Update run record with completion stats or failure details."""
    conn.execute(
        "UPDATE runs SET status=?, raw_count=?, relevant_count=?, completed_at=?, error_message=? WHERE run_id=?",
        (status, raw_count, relevant_count, completed_at, error_message, run_id)
    )
    conn.commit()

def insert_raw_items(conn: sqlite3.Connection, items: list[RawItem], run_id: str) -> None:
    """Store filtered items in the database, assigning the current run_id."""
    for item in items:
        conn.execute(
            "INSERT INTO raw_items (id, run_id, source_name, title, link, published_at, summary, ingested_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (item.id, run_id, item.source_name, item.title, item.link, item.published_at, item.summary, item.ingested_at)
        )
    conn.commit()
