import pytest
from unittest.mock import patch
from src.agent_hub.pipeline import run_digest
from src.agent_hub.ingester import RawItem
from src.agent_hub.filter import FilterError

def _make_item(n):
    return RawItem(
        id=f"pipe-{n}",
        run_id="",
        source_name="Src",
        title=f"Item {n}",
        link=f"https://example.com/{n}",
        published_at="2026-04-25T08:00:00+00:00",
        summary="summary",
        ingested_at="2026-04-25T08:00:00+00:00"
    )

def test_run_status_success(tmp_db_conn):
    """DGST-04: runs table shows status=success on clean pipeline run."""
    item = _make_item(1)
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "google/gemini-3-flash-preview"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"):
        result = run_digest(conn=tmp_db_conn)

    assert result.startswith("\u2705")
    row = tmp_db_conn.execute("SELECT status, raw_count, relevant_count FROM runs").fetchone()
    assert row[0] == "success"
    assert row[1] == 1
    assert row[2] == 1

def test_run_status_failure(tmp_db_conn):
    """DGST-04: runs table shows status=failure on OpenRouter error."""
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[_make_item(1)]), \
         patch("src.agent_hub.pipeline.relevance_filter", side_effect=FilterError("OpenRouter unreachable")), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "google/gemini-3-flash-preview"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"):
        result = run_digest(conn=tmp_db_conn)

    assert result.startswith("\u274c")
    row = tmp_db_conn.execute("SELECT status, error_message FROM runs").fetchone()
    assert row[0] == "failure"
    assert "OpenRouter unreachable" in row[1]
