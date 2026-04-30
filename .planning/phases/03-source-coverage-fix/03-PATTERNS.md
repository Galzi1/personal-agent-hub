# Phase 3: Source Coverage Fix - Pattern Map

**Mapped:** 2026-04-27
**Files analyzed:** 4 source files + 2 test files
**Analogs found:** 4 / 4 (all files are modifications of existing code)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/agent_hub/filter.py` | service | transform | `src/agent_hub/filter.py` (self) | exact - modify in place |
| `src/agent_hub/pipeline.py` | orchestrator | request-response | `src/agent_hub/pipeline.py` (self) | exact - modify in place |
| `src/agent_hub/discord.py` | utility | transform | `src/agent_hub/discord.py` (self) | exact - modify in place |
| `tests/test_filter.py` | test | transform | `tests/test_filter.py` (self) | exact - extend in place |
| `tests/test_discord.py` | test | transform | `tests/test_discord.py` (self) | exact - extend in place |
| `tests/test_pipeline.py` | test | request-response | `tests/test_pipeline.py` (self) | exact - extend in place |

---

## Pattern Assignments

### `src/agent_hub/filter.py` (service, transform)

**Change:** Remove `items[:50]` hard cap; add recency window; raise safety cap to 150; add per-source logging.

**Imports pattern** (lines 1-3) - unchanged, no new imports needed for `datetime`/`timezone` since they live in `pipeline.py`; add them here for the recency helper:
```python
import json
import logging
from datetime import datetime, timezone, timedelta
import httpx
from src.agent_hub.ingester import RawItem
```

**Existing cap to replace** (line 44):
```python
# BEFORE (line 44) - remove this:
for i, item in enumerate(items[:50], 1):

# AFTER - raise cap, apply after recency window:
RECENCY_HOURS = 48
FILTER_CAP = 150

for i, item in enumerate(items[:FILTER_CAP], 1):
```

**Recency window helper** - new function, insert above `relevance_filter()`:
```python
RECENCY_HOURS = 48
FILTER_CAP = 150

def apply_recency_window(items: list[RawItem]) -> list[RawItem]:
    """Exclude items older than RECENCY_HOURS. Items with no published_at pass through."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENCY_HOURS)
    kept = []
    source_counts: dict[str, int] = {}
    for item in items:
        if item.published_at is None:
            kept.append(item)
        else:
            pub = datetime.fromisoformat(item.published_at)
            # Ensure tz-aware for comparison
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub >= cutoff:
                kept.append(item)
        source_counts[item.source_name] = source_counts.get(item.source_name, 0)
    # Log zeros for sources that had items but none survived
    return kept
```

**Datetime parsing pattern** - ingester stores dates as:
```python
# ingester.py line 51 - UTC ISO string production:
published_at = datetime(*parsed_date[:6], tzinfo=timezone.utc).isoformat()
# Result example: "2026-04-25T08:00:00+00:00"

# Parse back for comparison (use fromisoformat - works for both +00:00 and Z suffixes):
pub = datetime.fromisoformat(item.published_at)
if pub.tzinfo is None:
    pub = pub.replace(tzinfo=timezone.utc)
```

**Logger pattern** - matches `pipeline.py` lines 4 and 54:
```python
logger = logging.getLogger(__name__)

# Per-source logging after recency window:
logger.warning(f"{source_name}: 0 items in 48h window - skipped")

# Per-source logging after ingest (pipeline.py):
logger.info(f"{source['name']}: {len(items)} items fetched")

# Per-source logging after filter (pipeline.py):
logger.info(f"{source_name}: {n} items passed filter")
```

**Error handling pattern** - unchanged, reuse existing `FilterError` raise style (lines 75, 98):
```python
raise FilterError(f"HTTP call to OpenRouter failed after 2 attempts: {e}")
raise FilterError(f"Failed to parse OpenRouter response: {e}. Raw: {str(content_for_error)[:200]}")
```

---

### `src/agent_hub/pipeline.py` (orchestrator, request-response)

**Changes:** (1) log per-source item counts after ingest; (2) apply recency window before filter call; (3) compute contributing-source breakdown from `relevant_items`; (4) pass breakdown to `format_digest()` instead of raw `source_count`.

**Existing ingest loop** (lines 44-55) - extend with logging:
```python
# BEFORE:
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
        logger.warning(f"Failed to fetch {source['name']}: {e}")

# AFTER (add logger.info call, remove source_count counter):
all_items = []
for source in sources:
    if not source.get("enabled"):
        continue
    try:
        items = fetch_feed(source["name"], source["url"])
        logger.info(f"{source['name']}: {len(items)} items fetched")
        all_items.extend(items)
    except IngestionError as e:
        logger.warning(f"Failed to fetch {source['name']}: {e}")
```

**Recency window call** - insert between ingest and filter (around line 57):
```python
# After ingest, before relevance_filter:
from src.agent_hub.filter import relevance_filter, apply_recency_window

windowed_items = apply_recency_window(all_items)
raw_count = len(all_items)  # keep original raw count for stats
relevant_items = relevance_filter(windowed_items, models["relevance"], api_key)
```

**Contributing-source breakdown** - derive from `relevant_items` in memory (no DB query needed per CONTEXT.md code_context):
```python
# After relevance_filter returns:
source_breakdown: dict[str, int] = {}
for item in relevant_items:
    source_breakdown[item.source_name] = source_breakdown.get(item.source_name, 0) + 1

# Log per-source pass counts:
for src_name, count in source_breakdown.items():
    logger.info(f"{src_name}: {count} items passed filter")
```

**format_digest() call site** (line 70) - replace `source_count` with `source_breakdown`:
```python
# BEFORE (line 70):
messages = format_digest(relevant_items, run_num, dt, run_id, raw_count, source_count)

# AFTER:
messages = format_digest(relevant_items, run_num, dt, run_id, raw_count, source_breakdown)
```

**Exception handler pattern** - unchanged (lines 82-91), reference only:
```python
except Exception as e:
    completed_at = datetime.now(timezone.utc).isoformat()
    try:
        current_raw = locals().get("all_items", [])
        raw_count = len(current_raw) if isinstance(current_raw, list) else 0
        complete_run(conn, run_id, "failure", raw_count, 0, completed_at, str(e))
    except Exception:
        pass
    return format_failure(run_num, str(e), run_id, dt)
```

---

### `src/agent_hub/discord.py` (utility, transform)

**Changes:** Update `format_success()` to accept `source_breakdown: dict[str, int]` and produce new multi-line format; update `format_digest()` signature to pass `source_breakdown` through; add coverage warning when <3 sources.

**Existing constants** (lines 4-9) - unchanged:
```python
CHECKMARK = "\u2705"
CROSSMARK = "\u274c"
WARNING   = "\u26a0\ufe0f"
ARROW     = "\u2192"
NEWSPAPER = "\U0001f4f0"
CHUNK_LIMIT = 1800
```

**format_success() replacement** - new signature and body:
```python
COVERAGE_THRESHOLD = 3

def format_success(
    run_num: int,
    raw: int,
    relevant: int,
    source_breakdown: dict[str, int],
    dt: datetime,
    run_id: str = "unknown",
) -> str:
    """Format success header with per-source breakdown and optional coverage warning."""
    ts = dt.strftime("%Y-%m-%d %H:%M")
    contributing = len(source_breakdown)
    low_coverage = contributing < COVERAGE_THRESHOLD

    status_line = (
        f"{CHECKMARK} Run #{run_num} - {ts}\n"
        f"{raw} fetched {ARROW} {relevant} relevant from {contributing} sources"
        + (" \u26a0\ufe0f" if low_coverage else "")
    )
    breakdown_parts = ", ".join(f"{name}: {count}" for name, count in source_breakdown.items())
    breakdown_line = f"({breakdown_parts})"

    lines = [status_line, breakdown_line]
    if low_coverage:
        lines.append(f"\u26a0\ufe0f Only {contributing} sources represented - check filters")
    lines.append(f"Run ID: {run_id}")
    return "\n".join(lines)
```

**Approved output format** (from CONTEXT.md specifics - exact format for tests):
```
✅ Run #5 - 2026-04-28 09:00
18 fetched → 9 relevant from 4 sources
(OpenAI Blog: 3, TestingCatalog: 3, Simon Willison: 2, Latent Space: 1)
Run ID: run-5-2026-04-28
```

```
✅ Run #5 - 2026-04-28 09:00
11 fetched → 4 relevant from 2 sources ⚠️
(OpenAI Blog: 3, Latent Space: 1)
⚠️ Only 2 sources represented - check filters
Run ID: run-5-2026-04-28
```

**format_digest() signature update** - change `source_count: int` to `source_breakdown: dict[str, int]`:
```python
# BEFORE (lines 27-34):
def format_digest(
    items: list,
    run_num: int,
    dt: datetime,
    run_id: str,
    raw_count: int,
    source_count: int,
) -> list[str]:

# AFTER:
def format_digest(
    items: list,
    run_num: int,
    dt: datetime,
    run_id: str,
    raw_count: int,
    source_breakdown: dict[str, int],
) -> list[str]:
    header = format_success(run_num, raw_count, len(items), source_breakdown, dt, run_id)
    # rest of chunking logic unchanged (lines 42-57)
```

**format_failure() and format_no_items()** - DO NOT change (Phase 1 D-08 locked):
```python
# Lines 16-24 remain exactly as-is
def format_failure(run_num: int, error: str, run_id: str, dt: datetime) -> str: ...
def format_no_items(run_num: int, dt: datetime, run_id: str = "unknown") -> str: ...
```

---

### `tests/test_filter.py` (test, transform)

**Changes:** Add three new tests for recency window. Existing tests unchanged.

**Item factory pattern** (lines 5-15) - extend with `published_at` variants:
```python
def _make_item(n, source="Test Feed", published_at=None):
    return RawItem(
        id=f"test-id-{n}",
        run_id="",
        source_name=source,
        title=f"Test item {n}",
        link=f"https://example.com/{n}",
        published_at=published_at,
        summary=f"summary {n}",
        ingested_at="2026-04-25T08:00:00+00:00"
    )
```

**New recency window tests - pattern to follow:**
```python
from datetime import datetime, timezone, timedelta
from src.agent_hub.filter import apply_recency_window

def test_recency_window_excludes_old_items():
    """D-01: Items older than 48h are excluded from filter input."""
    old_ts = (datetime.now(timezone.utc) - timedelta(hours=49)).isoformat()
    old_item = _make_item(1, published_at=old_ts)
    result = apply_recency_window([old_item])
    assert result == []

def test_recency_window_includes_recent_items():
    """D-01: Items within 48h window are kept."""
    recent_ts = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    recent_item = _make_item(2, published_at=recent_ts)
    result = apply_recency_window([recent_item])
    assert len(result) == 1

def test_recency_window_passes_none_published_at():
    """D-01: Items with published_at=None pass through (conservative inclusion)."""
    item = _make_item(3, published_at=None)
    result = apply_recency_window([item])
    assert len(result) == 1
    assert result[0].id == "test-id-3"
```

---

### `tests/test_discord.py` (test, transform)

**Changes:** Update existing `format_digest` and `format_success` call sites to use `source_breakdown: dict[str, int]`; add tests for breakdown line, coverage warning.

**Updated helper factory** - add `source` param (already present in `_make_discord_item`, lines 6-16):
```python
def _make_discord_item(title="GPT-5 announced", source="OpenAI Blog", url="https://openai.com/gpt5"):
    # unchanged - already accepts source param
```

**Existing call sites to update** - all `format_digest(..., source_count=N)` calls become `source_breakdown={"Source": N}`:
```python
# BEFORE (line 41):
result = format_digest([item], run_num=4, dt=..., run_id="run-4-2026-04-26", raw_count=12, source_count=7)

# AFTER:
result = format_digest([item], run_num=4, dt=..., run_id="run-4-2026-04-26", raw_count=12,
                       source_breakdown={"OpenAI Blog": 1})
```

**New tests to add:**
```python
def test_format_digest_shows_source_breakdown():
    """D-05: Success header includes per-source breakdown line."""
    item = _make_discord_item(source="OpenAI Blog")
    result = format_digest([item], run_num=5, dt=datetime(2026, 4, 28, 9, 0),
                           run_id="run-5-2026-04-28", raw_count=18,
                           source_breakdown={"OpenAI Blog": 3, "TestingCatalog": 3})
    assert "(OpenAI Blog: 3, TestingCatalog: 3)" in result[0]

def test_format_digest_coverage_warning_below_threshold():
    """D-09: Warning line appears when fewer than 3 sources contribute."""
    item = _make_discord_item(source="OpenAI Blog")
    result = format_digest([item], run_num=5, dt=datetime(2026, 4, 28, 9, 0),
                           run_id="run-5-2026-04-28", raw_count=11,
                           source_breakdown={"OpenAI Blog": 3, "Latent Space": 1})
    assert "\u26a0\ufe0f" in result[0]
    assert "Only 2 sources represented" in result[0]

def test_format_digest_no_warning_at_threshold():
    """D-08: No warning when exactly 3 sources contribute."""
    items = [_make_discord_item(source=s) for s in ["A", "B", "C"]]
    result = format_digest(items, run_num=1, dt=datetime(2026, 4, 28, 9, 0),
                           run_id="run-1", raw_count=10,
                           source_breakdown={"A": 1, "B": 1, "C": 1})
    assert "Only" not in result[0]
```

---

### `tests/test_pipeline.py` (test, request-response)

**Changes:** Update `patch("src.agent_hub.pipeline.relevance_filter", return_value=[item])` call sites; `source_count` variable gone - pipeline now derives `source_breakdown` internally. Tests that assert on `format_digest` call args must use `source_breakdown` kwarg.

**Existing multi-source mock pattern** (lines 24-34) - add multi-source items to test breakdown:
```python
# Make items with distinct source_name values to exercise contributing-source count:
def _make_item(n, source="Src"):
    return RawItem(
        id=f"pipe-{n}",
        run_id="",
        source_name=source,   # vary this for coverage tests
        title=f"Item {n}",
        link=f"https://example.com/{n}",
        published_at="2026-04-26T08:00:00+00:00",  # within 48h of test run
        summary="summary",
        ingested_at="2026-04-26T08:00:00+00:00"
    )
```

**Note on `published_at` in test items:** Existing `test_pipeline.py` items use `published_at="2026-04-25T08:00:00+00:00"` which is a fixed past date. When the recency window is applied in tests, this may fall outside 48h depending on test execution time. Tests that mock `relevance_filter` directly bypass the recency window and are unaffected. Tests exercising the full pipeline should either mock `apply_recency_window` or use a recent dynamic timestamp.

**Coverage warning pipeline integration test - new:**
```python
def test_run_digest_low_coverage_warning_in_discord(tmp_db_conn):
    """D-09: Discord message contains warning when <3 sources pass filter."""
    item = _make_item(1, source="OnlySource")
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.apply_recency_window", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "OnlySource", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "m"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        run_digest(conn=tmp_db_conn)
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    posted_content = call_args[1]["json"]["content"]
    assert "\u26a0\ufe0f" in posted_content
```

---

## Shared Patterns

### Datetime UTC-aware comparison
**Source:** `src/agent_hub/ingester.py` lines 38, 51 and `src/agent_hub/pipeline.py` lines 16, 63
**Apply to:** `apply_recency_window()` in `filter.py`
```python
# Production of UTC ISO strings:
datetime.now(timezone.utc).isoformat()
datetime(*parsed_date[:6], tzinfo=timezone.utc).isoformat()

# Parse back (fromisoformat handles +00:00 suffix produced by Python's isoformat()):
pub = datetime.fromisoformat(item.published_at)
if pub.tzinfo is None:
    pub = pub.replace(tzinfo=timezone.utc)
cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENCY_HOURS)
```

### Logger instantiation
**Source:** `src/agent_hub/pipeline.py` line 12
**Apply to:** `filter.py` (needs `logger = logging.getLogger(__name__)` added)
```python
import logging
logger = logging.getLogger(__name__)
```

### Named constants (no magic numbers)
**Source:** `src/agent_hub/discord.py` lines 4-9, Phase 0 D-17
**Apply to:** All new numeric thresholds in `filter.py` and `discord.py`
```python
RECENCY_HOURS = 48      # filter.py
FILTER_CAP = 150        # filter.py
COVERAGE_THRESHOLD = 3  # discord.py
```

### httpx.Client context manager pattern
**Source:** `src/agent_hub/filter.py` lines 62-68, `src/agent_hub/discord.py` lines 71-79
**Apply to:** No new HTTP calls needed in Phase 3 - existing pattern is reference only
```python
with httpx.Client(timeout=30.0) as client:
    resp = client.post(url, headers=headers, json=payload)
    resp.raise_for_status()
```

### Test mock: patch via module path
**Source:** `tests/test_pipeline.py` lines 24-32
**Apply to:** All new pipeline tests
```python
with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
     patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
     patch("src.agent_hub.pipeline.apply_recency_window", return_value=[item]), \
     patch("httpx.Client") as mock_client:
    mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
```

### Test mock: MagicMock httpx response
**Source:** `tests/test_filter.py` lines 21-23, `tests/test_pipeline.py` lines 21-23
```python
mock_resp = MagicMock()
mock_resp.status_code = 200
mock_resp.json.return_value = mock_openrouter_pass_response
mock_resp.raise_for_status.return_value = None
```

---

## No Analog Found

No files in Phase 3 are entirely new - all changes are modifications to existing files. No novel patterns required that lack codebase precedent.

---

## Metadata

**Analog search scope:** `src/agent_hub/`, `tests/`
**Files read:** `filter.py`, `pipeline.py`, `discord.py`, `ingester.py`, `tests/conftest.py`, `tests/test_filter.py`, `tests/test_discord.py`, `tests/test_pipeline.py`
**Pattern extraction date:** 2026-04-27
