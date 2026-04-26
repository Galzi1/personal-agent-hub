import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import logging

from src.agent_hub.config import load_sources, load_models, load_openrouter_key, load_discord_config
from src.agent_hub.ingester import fetch_feed, IngestionError
from src.agent_hub.filter import relevance_filter
from src.agent_hub.db import init_db, next_run_id, start_run, complete_run, insert_raw_items
from src.agent_hub.discord import format_digest, format_failure, format_no_items, post_to_discord

logger = logging.getLogger(__name__)

def run_digest(db_path: str | None = None, conn: sqlite3.Connection | None = None) -> str:
    """Orchestrate the AI news digest pipeline."""
    dt = datetime.now(timezone.utc)
    run_num = 0
    run_id = "run-0-unknown"
    own_conn = False

    if conn is None:
        # Default path relative to user profile
        default_db = Path.home() / ".microclaw" / "runtime" / "microclaw.db"
        db_path = db_path or str(default_db)
        # Ensure directory exists for the db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        own_conn = True

    try:
        # Step 1: config load
        sources = load_sources()
        models = load_models()
        api_key = load_openrouter_key()
        discord_token, channel_id = load_discord_config()

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
            return format_no_items(run_num, dt, run_id)
        else:
            messages = format_digest(relevant_items, run_num, dt, run_id, raw_count, source_count)
            posted = 0
            try:
                posted = post_to_discord(messages, discord_token, channel_id)
                complete_run(conn, run_id, "success", raw_count, relevant_count, completed_at, None)
                return f"posted {posted} messages"
            except Exception as e:
                logger.error(f"Discord API error after {posted}/{len(messages)} messages: {e}")
                complete_run(
                    conn, run_id, "partial", raw_count, relevant_count, completed_at,
                    f"Discord API failed on chunk {posted + 1}: {e}"
                )
                return f"partial: posted {posted}/{len(messages)} messages"

    except Exception as e:
        completed_at = datetime.now(timezone.utc).isoformat()
        try:
            # Persistent counts for failure runs if we have them
            current_raw = locals().get("all_items", [])
            raw_count = len(current_raw) if isinstance(current_raw, list) else 0
            complete_run(conn, run_id, "failure", raw_count, 0, completed_at, str(e))
        except Exception:
            pass
        return format_failure(run_num, str(e), run_id, dt)
    finally:
        if own_conn:
            conn.close()

if __name__ == "__main__":
    # Support direct execution for the MicroClaw schedule
    print(run_digest())
