import httpx
from unittest.mock import MagicMock, patch
from src.agent_hub.pipeline import run_digest
from src.agent_hub.ingester import RawItem
from src.agent_hub.filter import FilterError

def _make_item(n, source="Src"):
    return RawItem(
        id=f"pipe-{n}",
        run_id="",
        source_name=source,
        title=f"Item {n}",
        link=f"https://example.com/{n}",
        published_at="2026-04-26T08:00:00+00:00",
        summary="summary",
        ingested_at="2026-04-26T08:00:00+00:00"
    )

def test_run_status_success(tmp_db_conn):
    """DGST-04: runs table shows status=success; run_digest returns 'posted N messages'."""
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
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
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "google/gemini-3-flash-preview"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")):
        result = run_digest(conn=tmp_db_conn)

    assert result.startswith("❌")
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
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
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
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("posted")
    assert not result.startswith("✅")


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
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
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
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp_fail
        result = run_digest(conn=tmp_db_conn)
    assert result.startswith("❌")
    row = tmp_db_conn.execute("SELECT status FROM runs").fetchone()
    assert row[0] == "failure"


def test_run_digest_low_coverage_warning_in_discord(tmp_db_conn):
    """D-09: Discord message contains coverage warning when <3 sources pass filter."""
    item = _make_item(1, source="OnlySource")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "OnlySource", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        run_digest(conn=tmp_db_conn)
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    posted_content = call_args[1]["json"]["content"]
    assert "⚠️" in posted_content
    assert "Only 1 sources represented" in posted_content


def test_run_digest_multi_source_no_warning(tmp_db_conn):
    """D-08: No warning in Discord message when 3+ distinct sources contribute."""
    items = [_make_item(i, source=s) for i, s in enumerate(["Src A", "Src B", "Src C"])]
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    sources_cfg = [{"name": s, "url": "u", "enabled": True} for s in ["Src A", "Src B", "Src C"]]
    with patch("src.agent_hub.pipeline.fetch_feed", side_effect=lambda name, url: [next(i for i in items if i.source_name == name)]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=items), \
         patch("src.agent_hub.pipeline.apply_recency_window", side_effect=lambda x: x), \
         patch("src.agent_hub.pipeline.load_sources", return_value=sources_cfg), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        run_digest(conn=tmp_db_conn)
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    posted_content = call_args[1]["json"]["content"]
    assert "Only" not in posted_content
