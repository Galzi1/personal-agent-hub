from datetime import datetime
from src.agent_hub.discord import format_success, format_failure, format_no_items, format_digest
from src.agent_hub.ingester import RawItem


def _make_discord_item(title="GPT-5 announced", source="OpenAI Blog", url="https://openai.com/gpt5"):
    return RawItem(
        id="test-1",
        run_id="",
        source_name=source,
        title=title,
        link=url,
        published_at=None,
        summary="",
        ingested_at="2026-04-26T08:00:00Z"
    )

def test_format_success():
    """DGST-04: Success format matches D-08 spec exactly including -> arrow and emoji."""
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_success(run_num=42, raw=18, relevant=12, sources=7, dt=dt)
    assert result == "\u2705 Run #42 - 2026-04-25 08:01\n18 fetched \u2192 12 relevant items from 7 sources\nRun ID: unknown"

def test_format_failure():
    """DGST-04: Failure format matches D-08 spec exactly including Run ID: line."""
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_failure(run_num=43, error="OpenRouter unreachable", run_id="run-43-2026-04-25", dt=dt)
    assert result == "\u274c Run #43 failed - 2026-04-25 08:01\nOpenRouter unreachable\nRun ID: run-43-2026-04-25"

def test_format_no_items():
    """DGST-04: No-items format matches D-08 spec exactly including warning emoji."""
    dt = datetime(2026, 4, 26, 8, 1)
    result = format_no_items(run_num=44, dt=dt)
    assert result == "\u26a0\ufe0f Run #44 - 2026-04-26 08:01\n0 relevant items (all sources returned no new AI content)\nRun ID: unknown"


def test_format_digest_basic():
    """D-06, D-10: First chunk has status header + intro + bullet item."""
    item = _make_discord_item()
    result = format_digest([item], run_num=4, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-4-2026-04-26", raw_count=12, source_count=7)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert "\U0001f4f0 Today\u2019s AI updates:" in result[0]
    assert "\u2022 GPT-5 announced [OpenAI Blog]" in result[0]
    assert "<https://openai.com/gpt5>" in result[0]


def test_format_digest_truncates_title():
    """D-02: Titles longer than 80 chars are truncated to 80 chars."""
    long_title = "A" * 100
    item = _make_discord_item(title=long_title)
    result = format_digest([item], run_num=1, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-1", raw_count=1, source_count=1)
    assert "A" * 80 in result[0]
    assert "A" * 81 not in result[0]


def test_format_digest_suppresses_link_preview():
    """D-01: URLs are wrapped in angle brackets to suppress Discord link embeds."""
    item = _make_discord_item(url="https://example.com/article")
    result = format_digest([item], run_num=1, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-1", raw_count=1, source_count=1)
    assert "<https://example.com/article>" in result[0]


def test_format_digest_splits_chunks():
    """D-09: Accumulation exceeding 1800 chars produces multiple messages."""
    items = [
        _make_discord_item(
            title=f"{'AI News Story Number ' + str(i)} with a moderately long headline",
            source="Feed",
            url=f"https://example.com/story/{i}"
        )
        for i in range(20)
    ]
    result = format_digest(items, run_num=1, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-1", raw_count=20, source_count=1)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 1800 + 200
