from datetime import datetime
from src.agent_hub.discord import format_success, format_failure, format_no_items

def test_format_success():
    """DGST-04: Success format matches D-08 spec exactly including -> arrow and emoji."""
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_success(run_num=42, raw=18, relevant=12, sources=7, dt=dt)
    assert result == "\u2705 Run #42 - 2026-04-25 08:01\n18 fetched \u2192 12 relevant items from 7 sources"

def test_format_failure():
    """DGST-04: Failure format matches D-08 spec exactly including Run ID: line."""
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_failure(run_num=43, error="OpenRouter unreachable", run_id="run-43-2026-04-25", dt=dt)
    assert result == "\u274c Run #43 failed - 2026-04-25 08:01\nOpenRouter unreachable\nRun ID: run-43-2026-04-25"

def test_format_no_items():
    """DGST-04: No-items format matches D-08 spec exactly including warning emoji."""
    dt = datetime(2026, 4, 26, 8, 1)
    result = format_no_items(run_num=44, dt=dt)
    assert result == "\u26a0\ufe0f Run #44 - 2026-04-26 08:01\n0 relevant items (all sources returned no new AI content)"
