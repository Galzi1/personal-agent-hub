from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from src.agent_hub.ingester import RawItem
from src.agent_hub.filter import relevance_filter, apply_recency_window

def _make_item(n):
    return RawItem(
        id=f"test-id-{n}",
        run_id="",
        source_name="Test Feed",
        title=f"Test item {n}",
        link=f"https://example.com/{n}",
        published_at=None,
        summary=f"summary {n}",
        ingested_at="2026-04-25T08:00:00Z"
    )

def test_relevance_filter_pass(mock_openrouter_pass_response):
    """All items returned when OpenRouter returns all PASS verdicts."""
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_openrouter_pass_response
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = relevance_filter([item], "test-model", "test-key")

    assert len(result) == 1
    assert result[0].id == "test-id-1"

def test_relevance_filter_fail(mock_openrouter_fail_response):
    """Only PASS items returned when OpenRouter returns mixed verdicts."""
    items = [_make_item(1), _make_item(2)]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_openrouter_fail_response
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = relevance_filter(items, "test-model", "test-key")

    assert len(result) == 1
    assert result[0].title == "Test item 1"

def test_relevance_filter_empty():
    """Empty list returned without HTTP call when input is empty."""
    with patch("httpx.Client") as mock_client:
        result = relevance_filter([], "test-model", "test-key")
        assert result == []
        mock_client.return_value.__enter__.return_value.post.assert_not_called()


def _make_recency_item(n, source="Test Feed", published_at=None):
    return RawItem(
        id=f"recency-{n}",
        run_id="",
        source_name=source,
        title=f"Recency item {n}",
        link=f"https://example.com/r/{n}",
        published_at=published_at,
        summary="summary",
        ingested_at="2026-04-25T08:00:00+00:00"
    )


def test_recency_window_excludes_old_items():
    """D-01: Items older than 48h are excluded."""
    old_ts = (datetime.now(timezone.utc) - timedelta(hours=49)).isoformat()
    result = apply_recency_window([_make_recency_item(1, published_at=old_ts)])
    assert result == []


def test_recency_window_includes_recent_items():
    """D-01: Items within 48h window are kept."""
    recent_ts = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    result = apply_recency_window([_make_recency_item(2, published_at=recent_ts)])
    assert len(result) == 1


def test_recency_window_passes_none_published_at():
    """D-01: Items with published_at=None pass through (conservative inclusion)."""
    result = apply_recency_window([_make_recency_item(3, published_at=None)])
    assert len(result) == 1
    assert result[0].id == "recency-3"


def test_recency_window_mixed_items():
    """D-01: Only recent and None-dated items survive."""
    old_ts = (datetime.now(timezone.utc) - timedelta(hours=73)).isoformat()
    recent_ts = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
    items = [
        _make_recency_item(1, published_at=old_ts),
        _make_recency_item(2, published_at=recent_ts),
        _make_recency_item(3, published_at=None),
    ]
    result = apply_recency_window(items)
    assert len(result) == 2
    assert result[0].id == "recency-2"
    assert result[1].id == "recency-3"
