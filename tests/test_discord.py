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
    """D-05: Success format shows per-source breakdown (no warning at 3 sources)."""
    dt = datetime(2026, 4, 25, 8, 1)
    bd = {"Feed A": 3, "Feed B": 2, "Feed C": 2}
    result = format_success(run_num=42, raw=18, relevant=12, source_breakdown=bd, dt=dt, run_id="run-42")
    assert "✅ Run #42 - 2026-04-25 08:01" in result
    assert "18 fetched → 12 relevant from 3 sources" in result
    assert "(Feed A: 3, Feed B: 2, Feed C: 2)" in result
    assert "Run ID: run-42" in result
    assert "Only" not in result

def test_format_failure():
    """DGST-04: Failure format matches D-08 spec exactly including Run ID: line."""
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_failure(run_num=43, error="OpenRouter unreachable", run_id="run-43-2026-04-25", dt=dt)
    assert result == "❌ Run #43 failed - 2026-04-25 08:01\nOpenRouter unreachable\nRun ID: run-43-2026-04-25"

def test_format_no_items():
    """DGST-04: No-items format matches D-08 spec exactly including warning emoji."""
    dt = datetime(2026, 4, 26, 8, 1)
    result = format_no_items(run_num=44, dt=dt)
    assert result == "⚠️ Run #44 - 2026-04-26 08:01\n0 relevant items (all sources returned no new AI content)\nRun ID: unknown"


def test_format_digest_basic():
    """D-06, D-10: First chunk has status header + intro + bullet item."""
    item = _make_discord_item()
    result = format_digest([item], run_num=4, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-4-2026-04-26", raw_count=12,
                           source_breakdown={"OpenAI Blog": 1, "Feed B": 1, "Feed C": 1})
    assert isinstance(result, list)
    assert len(result) >= 1
    assert "\U0001f4f0 Today’s AI updates:" in result[0]
    assert "• GPT-5 announced [OpenAI Blog]" in result[0]
    assert "<https://openai.com/gpt5>" in result[0]


def test_format_digest_truncates_title():
    """D-02: Titles longer than 80 chars are truncated to 80 chars."""
    long_title = "A" * 100
    item = _make_discord_item(title=long_title)
    result = format_digest([item], run_num=1, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-1", raw_count=1,
                           source_breakdown={"OpenAI Blog": 1, "Feed B": 1, "Feed C": 1})
    assert "A" * 80 in result[0]
    assert "A" * 81 not in result[0]


def test_format_digest_suppresses_link_preview():
    """D-01: URLs are wrapped in angle brackets to suppress Discord link embeds."""
    item = _make_discord_item(url="https://example.com/article")
    result = format_digest([item], run_num=1, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-1", raw_count=1,
                           source_breakdown={"OpenAI Blog": 1, "Feed B": 1, "Feed C": 1})
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
                           run_id="run-1", raw_count=20,
                           source_breakdown={"Feed": 1, "Feed B": 1, "Feed C": 1})
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 1800 + 200


def test_format_success_coverage_warning_below_threshold():
    """D-09: Warning line appears when fewer than 3 sources contribute."""
    dt = datetime(2026, 4, 28, 9, 0)
    bd = {"OpenAI Blog": 3, "Latent Space": 1}
    result = format_success(run_num=5, raw=11, relevant=4, source_breakdown=bd, dt=dt, run_id="run-5-2026-04-28")
    assert "11 fetched → 4 relevant from 2 sources ⚠️" in result
    assert "(OpenAI Blog: 3, Latent Space: 1)" in result
    assert "⚠️ Only 2 sources represented - check filters" in result
    assert "Run ID: run-5-2026-04-28" in result


def test_format_success_no_warning_at_threshold():
    """D-08: No warning when exactly 3 sources contribute."""
    dt = datetime(2026, 4, 28, 9, 0)
    bd = {"A": 1, "B": 1, "C": 1}
    result = format_success(run_num=1, raw=10, relevant=3, source_breakdown=bd, dt=dt)
    assert "Only" not in result
    assert "⚠️" not in result.split("\n", 1)[1]


def test_format_digest_shows_source_breakdown():
    """D-05: Success header includes per-source breakdown line."""
    item = _make_discord_item(source="OpenAI Blog")
    result = format_digest([item], run_num=5, dt=datetime(2026, 4, 28, 9, 0),
                           run_id="run-5-2026-04-28", raw_count=18,
                           source_breakdown={"OpenAI Blog": 3, "TestingCatalog": 3, "Simon Willison": 2})
    assert "(OpenAI Blog: 3, TestingCatalog: 3, Simon Willison: 2)" in result[0]


def test_format_digest_coverage_warning_below_threshold():
    """D-09: Warning line appears in digest when fewer than 3 sources contribute."""
    item = _make_discord_item(source="OpenAI Blog")
    result = format_digest([item], run_num=5, dt=datetime(2026, 4, 28, 9, 0),
                           run_id="run-5-2026-04-28", raw_count=11,
                           source_breakdown={"OpenAI Blog": 3, "Latent Space": 1})
    assert "⚠️" in result[0]
    assert "Only 2 sources represented" in result[0]
