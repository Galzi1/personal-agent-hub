import sqlite3
from datetime import datetime
from src.agent_hub.db import init_db, next_run_id, start_run, complete_run, insert_raw_items
from src.agent_hub.ingester import RawItem

def test_run_id_format(tmp_db_conn):
    """DGST-04: next_run_id returns format run-{N}-{YYYY-MM-DD} on empty DB."""
    init_db(tmp_db_conn)
    run_num, run_id = next_run_id(tmp_db_conn)
    assert run_num == 1
    assert run_id.startswith("run-1-")
    parts = run_id.split("-")
    assert len(parts) == 5  # run, 1, YYYY, MM, DD

def test_insert_raw_item(tmp_db_conn):
    """Inserting one RawItem results in row count 1 in raw_items table."""
    init_db(tmp_db_conn)
    run_num, run_id = next_run_id(tmp_db_conn)
    start_run(tmp_db_conn, run_id, run_num, "2026-04-25T08:00:00+00:00")
    item = RawItem(
        id="test-id-1",
        run_id="",
        source_name="Test",
        title="Test Item",
        link="https://example.com",
        published_at=None,
        summary="test summary",
        ingested_at="2026-04-25T08:00:00+00:00"
    )
    insert_raw_items(tmp_db_conn, [item], run_id)
    count = tmp_db_conn.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0]
    assert count == 1
    row = tmp_db_conn.execute("SELECT run_id FROM raw_items WHERE id='test-id-1'").fetchone()
    assert row[0] == run_id

def test_runs_crud(tmp_db_conn):
    """DGST-04: start_run + complete_run produces correct row in runs table."""
    init_db(tmp_db_conn)
    run_num, run_id = next_run_id(tmp_db_conn)
    start_run(tmp_db_conn, run_id, run_num, "2026-04-25T08:00:00+00:00")
    complete_run(tmp_db_conn, run_id, "success", 18, 12, "2026-04-25T08:01:00+00:00", None)
    row = tmp_db_conn.execute("SELECT status, raw_count, relevant_count FROM runs WHERE run_id=?", (run_id,)).fetchone()
    assert row[0] == "success"
    assert row[1] == 18
    assert row[2] == 12
