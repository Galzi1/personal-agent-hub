# Phase 2: Thin Digest - Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 6 (4 modified, 2 test files updated)
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/agent_hub/discord.py` | utility (format + HTTP poster) | request-response | `src/agent_hub/filter.py` (httpx pattern) + existing `discord.py` | exact |
| `src/agent_hub/pipeline.py` | orchestrator | request-response | `src/agent_hub/pipeline.py` (Step 6 modify) | self-analog (in-place modification) |
| `src/agent_hub/config.py` | config | CRUD | `src/agent_hub/config.py` (load_openrouter_key) | self-analog (extend with new loader) |
| `src/agent_hub/db.py` | model/data | CRUD | `src/agent_hub/db.py` (complete_run) | self-analog (comment/docstring only) |
| `tests/test_discord.py` | test | request-response | `tests/test_filter.py` + existing `test_discord.py` | exact |
| `tests/test_pipeline.py` | test | request-response | `tests/test_pipeline.py` + `tests/test_filter.py` | exact |

## Pattern Assignments

---

### `src/agent_hub/discord.py` (utility, request-response)

**Analogs:** `src/agent_hub/discord.py` (existing format helpers) + `src/agent_hub/filter.py` (httpx.Client pattern)

**Imports pattern** - current `discord.py` lines 1-6 + additions needed:
```python
from datetime import datetime
import httpx

CHECKMARK = "\u2705"
CROSSMARK = "\u274c"
WARNING   = "\u26a0\ufe0f"
ARROW     = "\u2192"
NEWSPAPER = "\U0001f4f0"   # new
CHUNK_LIMIT = 1800          # new
```

**Core format_digest() pattern** - modelled on existing `format_success()` (lines 8-11) + RESEARCH.md Pattern 1:
```python
def format_digest(
    items: list,          # list[RawItem]
    run_num: int,
    dt: datetime,
    run_id: str,
    raw_count: int,
    source_count: int,
) -> list[str]:
    """Format items into one or more Discord-ready message strings (max ~1800 chars each)."""
    header = format_success(run_num, raw_count, len(items), source_count, dt, run_id)
    intro = f"\n{NEWSPAPER} Today's AI updates:"
    chunks: list[str] = []
    current = header + intro

    for item in items:
        title = item.title[:80] if len(item.title) > 80 else item.title
        line = f"\n\u2022 {title} [{item.source_name}]\n  <{item.link}>"
        if len(current) + len(line) > CHUNK_LIMIT:
            chunks.append(current)
            current = line.lstrip("\n")
        else:
            current += line

    chunks.append(current)
    return chunks
```

**Core post_to_discord() pattern** - directly from `filter.py` httpx.Client pattern (lines 62-68):
```python
# filter.py lines 62-68 (exact model to copy):
with httpx.Client(timeout=90.0) as client:
    resp = client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    resp.raise_for_status()

# Discord adaptation (RESEARCH.md Pattern 2):
def post_to_discord(messages: list[str], token: str, channel_id: str) -> int:
    """Post messages to Discord. Returns count of successfully posted messages."""
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    posted = 0
    with httpx.Client(timeout=30.0) as client:
        for msg in messages:
            resp = client.post(url, headers=headers, json={"content": msg})
            resp.raise_for_status()
            posted += 1
    return posted
```

**Error handling pattern** - follows `filter.py` lines 59-75 (`last_exc`, raise on failure). For `post_to_discord`, error handling lives in `pipeline.py` caller (see below), not inside the function - keeps the helper simple and testable.

---

### `src/agent_hub/pipeline.py` (orchestrator, request-response)

**Analog:** `src/agent_hub/pipeline.py` (self-modification of Step 6)

**Imports change** - current lines 6-10, add discord imports:
```python
# current line 10:
from src.agent_hub.discord import format_success, format_failure, format_no_items
# replace with:
from src.agent_hub.discord import format_digest, format_failure, format_no_items, post_to_discord
# and add to Step 1 config loader:
from src.agent_hub.config import load_sources, load_models, load_openrouter_key, load_discord_config
```

**Step 1 config pattern** - extend existing pattern (lines 32-34):
```python
# current:
sources = load_sources()
models = load_models()
api_key = load_openrouter_key()
# add:
discord_token, channel_id = load_discord_config()
```

**Step 6 Notify pattern** - replace current lines 64-70 with:
```python
# Step 6: Notify
if relevant_count == 0:
    complete_run(conn, run_id, "no_items", raw_count, 0, completed_at, None)
    return format_no_items(run_num, dt, run_id)
else:
    messages = format_digest(relevant_items, run_num, dt, run_id, raw_count, source_count)
    posted = 0
    try:
        posted = post_to_discord(messages, discord_token, channel_id)
        complete_run(conn, run_id, "success", raw_count, relevant_count, completed_at, None)
        return f"posted {posted} messages"
    except Exception as e:
        logger.error(f"Discord API error after {posted}/{len(messages)} messages: {e}")
        complete_run(conn, run_id, "partial", raw_count, relevant_count, completed_at,
                     f"Discord API failed on chunk {posted + 1}: {e}")
        return f"partial: posted {posted}/{len(messages)} messages"
```

**Outer exception handler** - current lines 72-81 unchanged; handles pipeline-level failures (OpenRouter, ingest) with `format_failure()` return.

---

### `src/agent_hub/config.py` (config, CRUD)

**Analog:** `src/agent_hub/config.py` - `load_openrouter_key()` (lines 34-49) is the exact pattern to copy.

**load_discord_config() pattern** - copy structure of `load_openrouter_key()` exactly:
```python
# load_openrouter_key() - lines 34-49 (model to copy):
def load_openrouter_key() -> str:
    """Load OpenRouter API key from config/microclaw.config.yaml."""
    path = Path("config/microclaw.config.yaml")
    if not path.exists():
        raise ConfigError(f"Secret config not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            key = data.get("openrouter_api_key", "").strip()
            if not key:
                raise ConfigError("openrouter_api_key missing or empty in microclaw.config.yaml")
            return key
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load OpenRouter key: {e}")

# New function - same structure, different keys:
def load_discord_config() -> tuple[str, str]:
    """Return (bot_token, channel_id) from config/microclaw.config.yaml."""
    path = Path("config/microclaw.config.yaml")
    if not path.exists():
        raise ConfigError(f"Secret config not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            token = data["channels"]["discord"]["accounts"]["main"]["bot_token"]
            if not token or not token.strip():
                raise ConfigError("channels.discord.accounts.main.bot_token missing in microclaw.config.yaml")
            channel_id = data["channels"]["discord"].get("channel_id", "").strip()
            if not channel_id:
                raise ConfigError("channels.discord.channel_id missing in microclaw.config.yaml")
            return token.strip(), channel_id
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load Discord config: {e}")
```

---

### `src/agent_hub/db.py` (model/data, CRUD)

**Analog:** `src/agent_hub/db.py` - `complete_run()` (lines 48-61) and `CREATE_RUNS` (lines 17-26).

**Modification required:** Comment-only change to document `partial` as a valid status. SQLite does not enforce CHECK constraints by default, so no schema migration is needed - `complete_run()` accepts any string for `status`.

**Pattern to follow** (lines 17-26 and 48-61):
```python
# CREATE_RUNS - add inline comment documenting allowed status values:
CREATE_RUNS = """CREATE TABLE IF NOT EXISTS runs (
    run_id         TEXT PRIMARY KEY,
    run_number     INTEGER NOT NULL,
    started_at     TEXT NOT NULL,
    completed_at   TEXT,
    status         TEXT,  -- running | success | no_items | failure | partial
    raw_count      INTEGER DEFAULT 0,
    relevant_count INTEGER DEFAULT 0,
    error_message  TEXT
)"""

# complete_run() - no signature change needed. "partial" is passed as the status string:
complete_run(conn, run_id, "partial", raw_count, relevant_count, completed_at, error_msg)
```

---

### `tests/test_discord.py` (test, request-response)

**Analog:** `tests/test_discord.py` (existing tests) + `tests/test_filter.py` (httpx mock pattern)

**Wave 0 fix pattern** - fix existing assertions to match actual `format_success` / `format_no_items` output (both now include `\nRun ID: ...` line):

```python
# test_discord.py lines 7-8 (currently failing - fix assertion):
def test_format_success():
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_success(run_num=42, raw=18, relevant=12, sources=7, dt=dt)
    # BEFORE (wrong): assert result == "\u2705 Run #42 - 2026-04-25 08:01\n18 fetched \u2192 12 relevant items from 7 sources"
    # AFTER (correct - matches discord.py line 11):
    assert result == "\u2705 Run #42 - 2026-04-25 08:01\n18 fetched \u2192 12 relevant items from 7 sources\nRun ID: unknown"

def test_format_no_items():
    dt = datetime(2026, 4, 26, 8, 1)
    result = format_no_items(run_num=44, dt=dt)
    # BEFORE (wrong): assert result == "\u26a0\ufe0f Run #44 - 2026-04-26 08:01\n0 relevant items (...)"
    # AFTER (correct - matches discord.py line 21):
    assert result == "\u26a0\ufe0f Run #44 - 2026-04-26 08:01\n0 relevant items (all sources returned no new AI content)\nRun ID: unknown"
```

**New test structure pattern** - from `test_filter.py` lines 18-32 (mock + assert on result):
```python
# test_filter.py lines 18-32 (model for new format_digest tests):
def test_relevance_filter_pass(mock_openrouter_pass_response):
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_openrouter_pass_response
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = relevance_filter([item], "test-model", "test-key")

    assert len(result) == 1

# New format_digest tests do NOT need httpx mock (format_digest is pure string logic):
def test_format_digest_basic():
    from src.agent_hub.discord import format_digest
    from src.agent_hub.ingester import RawItem
    from datetime import datetime
    item = RawItem(id="1", run_id="", source_name="OpenAI Blog",
                   title="GPT-5 announced", link="https://openai.com/gpt5",
                   published_at=None, summary="", ingested_at="2026-04-26T08:00:00Z")
    result = format_digest([item], run_num=4, dt=datetime(2026, 4, 26, 8, 0),
                           run_id="run-4-2026-04-26", raw_count=12, source_count=7)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert "\U0001f4f0 Today's AI updates:" in result[0]
    assert "\u2022 GPT-5 announced [OpenAI Blog]" in result[0]
    assert "<https://openai.com/gpt5>" in result[0]
```

---

### `tests/test_pipeline.py` (test, request-response)

**Analog:** `tests/test_pipeline.py` (existing tests) + `tests/test_filter.py` (httpx mock pattern lines 26-32)

**httpx mock pattern** - `test_filter.py` lines 26-27 is the exact model:
```python
with patch("httpx.Client") as mock_client:
    mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
```

**Updated existing test** - `test_run_status_success` (lines 19-33) needs Discord mock added and assertion changed:
```python
def test_run_status_success(tmp_db_conn):
    item = _make_item(1)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("src.agent_hub.pipeline.fetch_feed", return_value=[item]), \
         patch("src.agent_hub.pipeline.relevance_filter", return_value=[item]), \
         patch("src.agent_hub.pipeline.load_sources", return_value=[{"name": "S", "url": "u", "enabled": True}]), \
         patch("src.agent_hub.pipeline.load_models", return_value={"relevance": "google/gemini-3-flash-preview"}), \
         patch("src.agent_hub.pipeline.load_openrouter_key", return_value="test-key"), \
         patch("src.agent_hub.pipeline.load_discord_config", return_value=("tok", "123456")), \
         patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
        result = run_digest(conn=tmp_db_conn)
    # BEFORE: assert result.startswith("\u2705")
    # AFTER:
    assert result.startswith("posted")
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    row = tmp_db_conn.execute("SELECT status FROM runs").fetchone()
    assert row[0] == "success"
```

**New partial test pattern** - modelled on `test_run_status_failure` (lines 35-47):
```python
def test_run_digest_partial_on_discord_failure(tmp_db_conn):
    item = _make_item(1)
    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403", request=MagicMock(), response=MagicMock()
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
    assert result.startswith("partial")
    row = tmp_db_conn.execute("SELECT status FROM runs").fetchone()
    assert row[0] == "partial"
```

---

## Shared Patterns

### httpx.Client context manager (HTTP calls)
**Source:** `src/agent_hub/filter.py` lines 62-68
**Apply to:** `discord.py` `post_to_discord()`, and all new Discord API test mocks
```python
with httpx.Client(timeout=30.0) as client:
    resp = client.post(url, headers=headers, json=payload)
    resp.raise_for_status()
```

### Test mock for httpx.Client
**Source:** `tests/test_filter.py` lines 26-27
**Apply to:** All test functions that exercise `post_to_discord()` (test_pipeline.py new tests)
```python
with patch("httpx.Client") as mock_client:
    mock_client.return_value.__enter__.return_value.post.return_value = mock_resp
```

### ConfigError pattern (config loader)
**Source:** `src/agent_hub/config.py` lines 5-7 and 40-49
**Apply to:** `load_discord_config()` in `config.py`
```python
class ConfigError(Exception):
    """Raised when configuration is missing or malformed."""
    pass

# Re-raise pattern (lines 46-49):
except Exception as e:
    if isinstance(e, ConfigError):
        raise
    raise ConfigError(f"Failed to load ...: {e}")
```

### complete_run() call pattern (DB status update)
**Source:** `src/agent_hub/db.py` lines 48-61, used in `pipeline.py` lines 66-70
**Apply to:** New `"partial"` status call in pipeline.py Step 6
```python
complete_run(conn, run_id, "partial", raw_count, relevant_count, completed_at,
             f"Discord API failed on chunk {posted + 1}: {e}")
```

### RawItem factory helper in tests
**Source:** `tests/test_filter.py` lines 6-16 and `tests/test_pipeline.py` lines 7-17
**Apply to:** All new test functions in test_discord.py and test_pipeline.py that need item fixtures
```python
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
```

---

## No Analog Found

All Phase 2 files have close analogs in the existing codebase. No new file type or data flow is introduced.

---

## Metadata

**Analog search scope:** `src/agent_hub/`, `tests/`
**Files scanned:** 8 source files read in full
**Pattern extraction date:** 2026-04-26
