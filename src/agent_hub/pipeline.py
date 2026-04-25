import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import logging

from src.agent_hub.config import load_sources, load_models, load_openrouter_key
from src.agent_hub.ingester import fetch_feed, IngestionError
from src.agent_hub.filter import relevance_filter
from src.agent_hub.db import init_db, next_run_id, start_run, complete_run, insert_raw_items
from src.agent_hub.discord import format_success, format_failure, format_no_items

logger = logging.getLogger(__name__)

def run_digest(db_path: str | None = None, conn: sqlite3.Connection | None = None) -> str:
    """Orchestrate the AI news digest pipeline."""
    dt = datetime.now(timezone.utc)
    run_num = 0
    run_id = "run-0-unknown"
    own_conn = False

    if conn is None:
        db_path = db_path or r"C:\Users\galzi\.microclaw\runtime\microclaw.db"
        # Ensure directory exists for the db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        own_conn = True

    try:
        # Step 1: config load
        sources = load_sources()
        models = load_models()
        api_key = load_openrouter_key()

        # Step 2: DB setup
        init_db(conn)
        run_num, run_id = next_run_id(conn)
        start_run(conn, run_id, run_num, dt.isoformat())

        # Step 3: Ingest
        all_items = []
        source_count = 0
        for source in sources:
            if not source.get("enabled"):
                continue
            source_count += 1
            try:
                items = fetch_feed(source["name"], source["url"])
                all_items.extend(items)
            except IngestionError as e:
                # Per-source fail: warn and continue
                logger.warning(f"Failed to fetch {source['name']}: {e}")

        # Step 4: Filter
        raw_count = len(all_items)
        relevant_items = relevance_filter(all_items, models["relevance"], api_key)

        # Step 5: Persist
        insert_raw_items(conn, relevant_items, run_id)
        relevant_count = len(relevant_items)
        completed_at = datetime.now(timezone.utc).isoformat()

        # Step 6: Notify
        if relevant_count == 0:
            complete_run(conn, run_id, "no_items", raw_count, 0, completed_at, None)
            return format_no_items(run_num, dt)
        else:
            complete_run(conn, run_id, "success", raw_count, relevant_count, completed_at, None)
            return format_success(run_num, raw_count, relevant_count, source_count, dt)

    except Exception as e:
        completed_at = datetime.now(timezone.utc).isoformat()
        try:
            complete_run(conn, run_id, "failure", 0, 0, completed_at, str(e))
        except Exception:
            pass
        return format_failure(run_num, str(e), run_id, dt)
    finally:
        if own_conn:
            conn.close()

if __name__ == "__main__":
    # Support direct execution for the MicroClaw schedule
    print(run_digest())
