from unittest.mock import MagicMock, patch
from src.agent_hub.ingester import RawItem
from src.agent_hub.filter import relevance_filter

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
