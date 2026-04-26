import httpx
from unittest.mock import MagicMock, patch
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
    """DGST-04: runs table shows status=success; run_digest returns 'posted N messages'."""
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "google/gemini-3-flash-preview"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("bot-token", "123456789")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("posted")
    mock_client.return_value.__enter__.return_value.post.assert_called()
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
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")):
        result = run_digest(conn=tmp_db_conn)

    assert result.startswith("\u274c")
    row = tmp_db_conn.execute("SELECT status, error_message FROM runs").fetchone()
    assert row[0] == "failure"
    assert "OpenRouter unreachable" in row[1]


def test_run_digest_posts_to_discord(tmp_db_conn):
    """D-11, D-12: run_digest POSTs to Discord REST API with correct URL and Bot auth."""
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("my-bot-token", "987654321")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        run_digest(conn=tmp_db_conn)
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    assert call_args is not None
    assert "discord.com/api/v10/channels/987654321/messages" in call_args[0][0]
    assert call_args[1]["headers"]["Authorization"] == "Bot my-bot-token"


def test_run_digest_returns_confirmation(tmp_db_conn):
    """D-15: run_digest() returns a confirmation string, not a formatted Discord message."""
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("posted")
    assert not result.startswith("\u2705")


def test_run_digest_partial_on_discord_failure(tmp_db_conn):
    """D-16, D-17: mid-stream Discord failure (2nd message) marks run as partial."""
    item = _make_item(1)
    mock_resp_ok = MagicMock()
    mock_resp_ok.raise_for_status.return_value = None
    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403 Forbidden", request=MagicMock(), response=MagicMock()
    )
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("src.agent_hub.pipeline.format_digest", return_value=["msg1", "msg2"]), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = [mock_resp_ok, mock_resp_fail]
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("partial")
    row = tmp_db_conn.execute("SELECT status FROM runs").fetchone()
    assert row[0] == "partial"


def test_run_digest_failure_on_complete_discord_error(tmp_db_conn):
    """Discord complete failure (first message fails) marks run as failure."""
    item = _make_item(1)
    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403 Forbidden", request=MagicMock(), response=MagicMock()
    )
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp_fail
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("\u274c")
    row = tmp_db_conn.execute("SELECT status FROM runs").fetchone()
    assert row[0] == "failure"
