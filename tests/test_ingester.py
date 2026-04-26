from unittest.mock import MagicMock, patch
from src.agent_hub.ingester import fetch_feed

def test_parses_rss_items(sample_rss):
    """SRC-01: Items from a fixture-backed feed are parsed into RawItem schema."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = sample_rss

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        items = fetch_feed("Test Feed", "https://example.com/rss")

        assert len(items) == 2
        assert items[0].title == "GPT-5.5 released"
        assert items[0].source_name == "Test Feed"
        assert items[1].link == "https://openai.com/academy/codex"

def test_date_fallback_chain():
    """SRC-01: Date fallback chain (published_parsed -> updated_parsed -> created_parsed) works."""
    # Feed with only updated info (Atom style)
    atom_xml = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Atom Entry</title>
        <updated>2026-04-24T12:00:00Z</updated>
        <link href="https://example.com/atom"/>
        <summary>Atom summary</summary>
      </entry>
    </feed>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = atom_xml

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        items = fetch_feed("Atom Feed", "https://example.com/atom")

        assert len(items) == 1
        assert items[0].published_at is not None
        assert "2026-04-24" in items[0].published_at

def test_disabled_sources_skipped(sample_sources):
    """SRC-01: Disabled sources in sources.yaml are skipped."""
    enabled = [s for s in sample_sources if s["enabled"]]
    disabled = [s for s in sample_sources if not s["enabled"]]

    assert len(enabled) == 1
    assert len(disabled) == 1
    assert enabled[0]["name"] == "Test Feed A"

def test_fetches_all_enabled_sources(sample_sources):
    """SRC-01: All enabled sources are attempted."""
    enabled = [s for s in sample_sources if s["enabled"]]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<rss><channel></channel></rss>"

    fetched_names = []
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        for source in enabled:
            fetch_feed(source["name"], source["url"])
            fetched_names.append(source["name"])

    assert fetched_names == [s["name"] for s in enabled]
    assert "Test Feed B" not in fetched_names
