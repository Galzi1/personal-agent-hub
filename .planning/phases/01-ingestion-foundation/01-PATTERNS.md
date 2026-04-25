# Phase 1: Ingestion Foundation & Run Visibility - Pattern Map

**Mapped:** 2026-04-25
**Files analyzed:** 16 (10 source, 6 test/config)
**Analogs found:** 14 / 16 (2 new-pattern files with no codebase analog)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/agent_hub/__init__.py` | module-init | - | `spikes/spike_watchlist.py` (top-level module shape) | partial |
| `src/agent_hub/config.py` | utility | transform | `spikes/spike_openrouter.py` lines 13-43 | role-match |
| `src/agent_hub/ingester.py` | service | request-response | `spikes/spike_watchlist.py` lines 29-89 | exact |
| `src/agent_hub/filter.py` | service | request-response | `spikes/spike_openrouter.py` lines 76-116 | role-match |
| `src/agent_hub/db.py` | service | CRUD | `spikes/spike_openrouter.py` (no SQLite analog; DB schema from RESEARCH.md) | no analog |
| `src/agent_hub/pipeline.py` | service | request-response | `spikes/spike_watchlist.py` lines 92-166 (orchestration shape) | partial |
| `src/agent_hub/discord.py` | utility | transform | `spikes/spike_watchlist.py` (output formatting shape) | partial |
| `tests/conftest.py` | test | - | `spikes/spike_watchlist.py` (fixture data shape) | partial |
| `tests/test_ingester.py` | test | - | `spikes/spike_watchlist.py` lines 29-89 | role-match |
| `tests/test_filter.py` | test | - | `spikes/spike_openrouter.py` lines 76-116 | role-match |
| `tests/test_db.py` | test | - | no analog (new CRUD layer) | no analog |
| `tests/test_discord.py` | test | - | `spikes/spike_watchlist.py` (output formatting) | partial |
| `tests/test_pipeline.py` | test | - | `spikes/spike_watchlist.py` lines 92-166 | partial |
| `config/sources.yaml` | config | - | `config/models.yaml` | role-match |
| `config/models.yaml` | config (modify) | - | `config/models.yaml` (self) | exact |
| `pyproject.toml` | config | - | no pyproject.toml exists yet | no analog |

---

## Pattern Assignments

### `src/agent_hub/config.py` (utility, transform)

**Analog:** `spikes/spike_openrouter.py`

**Imports pattern** (lines 8-11):
```python
import yaml
import sys
from pathlib import Path
```

**Core YAML loading pattern** (lines 13-43):
```python
CONFIG_PATH = Path("config/microclaw.config.yaml")
MODELS_PATH = Path("config/models.yaml")

try:
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    OPENROUTER_KEY = cfg["openrouter_api_key"]
    if not OPENROUTER_KEY:
        raise ValueError(f"openrouter_api_key is empty in {CONFIG_PATH}")
except FileNotFoundError:
    print(f"Error: Configuration file not found at {CONFIG_PATH}")
    sys.exit(1)
except ValueError as e:
    print(f"Error loading configuration: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading config: {e}")
    sys.exit(1)

try:
    with open(MODELS_PATH) as f:
        models_cfg = yaml.safe_load(f)
    MODELS = {k: v["model"] for k, v in models_cfg["tasks"].items()}
except FileNotFoundError:
    print(f"Error: Models file not found at {MODELS_PATH}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading models: {e}")
    sys.exit(1)
```

**Key adaptation notes for `config.py`:**
- Replace `sys.exit(1)` calls with raising a typed exception (e.g., `ConfigError`) so the pipeline can catch and record a run failure rather than hard-exiting.
- Add a third loader for `config/sources.yaml` using the same `safe_load` pattern.
- Return typed objects: the YAML dict for sources, and a task-to-model-id dict for models.
- `config/microclaw.config.yaml` is at repo root currently - Pitfall 6 in RESEARCH.md: Plan 01-01 moves it to `config/`. Use `Path("config/microclaw.config.yaml")` as the canonical path.

---

### `src/agent_hub/ingester.py` (service, request-response)

**Analog:** `spikes/spike_watchlist.py`

**Imports pattern** (lines 1-9):
```python
import feedparser
import httpx
from datetime import datetime, timedelta, timezone
from time import mktime
import sys
```

**Core fetch-and-parse pattern** (lines 29-89):
```python
HEADERS = {"User-Agent": "PersonalAgentHub-Spike/0.1 (feed validation)"}

def fetch_feed(name: str, url: str) -> dict:
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "http_status": None,
        "total_entries": 0,
        "recent_entries": [],
        "error": None,
    }

    try:
        # Use httpx to fetch with proper headers and timeout
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url, headers=HEADERS)
        result["http_status"] = response.status_code

        if response.status_code != 200:
            result["status"] = f"HTTP {response.status_code}"
            result["error"] = f"Non-200 response: {response.status_code}"
            return result

        # Parse with feedparser - never call feedparser with the URL directly
        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            result["status"] = "PARSE_ERROR"
            result["error"] = str(feed.bozo_exception) if feed.bozo_exception else "Unknown parse error"
            return result

        result["total_entries"] = len(feed.entries)

        for entry in feed.entries:
            # Date fallback chain: published_parsed → updated_parsed → created_parsed
            published = None
            for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
                parsed_time = entry.get(date_field)
                if parsed_time:
                    published = datetime.fromtimestamp(mktime(parsed_time), tz=timezone.utc)
                    break

            result["recent_entries"].append({
                "title": entry.get("title", "[no title]"),
                "link": entry.get("link", "[no link]"),
                "published": published.isoformat() if published else None,
                "source": name,
            })

        result["status"] = "OK"
        return result

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        return result
```

**Key adaptation notes for `ingester.py`:**
- Replace the return dict with a `list[RawItem]` pydantic model (title, link, published_at, summary, source_name).
- Add `summary: entry.get("summary", "")` to the entry dict - the spike omits this but D-12 requires it.
- `source_name` replaces the spike's `source` key.
- `published_at` replaces `published` - keep as `isoformat()` string per D-12.
- The `httpx.Client` context manager pattern (lines 43-45) is the canonical form - copy verbatim.
- Anti-pattern guard: `feedparser.parse(response.text)` not `feedparser.parse(url)` - enforce this.

---

### `src/agent_hub/filter.py` (service, request-response)

**Analog:** `spikes/spike_openrouter.py`

**Imports and setup pattern** (lines 8-51):
```python
import httpx
import yaml
import time
import sys
from pathlib import Path

BASE_URL = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Personal Agent Hub Spike",
}
```

**Core OpenRouter chat call pattern** (lines 76-116):
```python
def chat(task_type: str, prompt: str, model_override: str | None = None) -> dict:
    global total_cost_usd
    check_spend()
    model = model_override or MODELS[task_type]
    start = time.monotonic()
    try:
        resp = httpx.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADERS,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
            },
            timeout=90,
        )
        resp.raise_for_status()
        elapsed = time.monotonic() - start
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError(f"Empty choices in response: {data.get('error', data)}")
        content = choices[0]["message"]["content"]
        usage = data.get("usage", {})
        cost = usage.get("cost", 0.0) or 0.0
        total_cost_usd += cost
        return {
            "status": "ok",
            "model": model,
            "content": content,
            "latency_s": round(elapsed, 2),
            "tokens": usage,
            "cost_usd": cost,
        }
    except Exception as e:
        return {
            "status": "error",
            "model": model,
            "error": str(e),
            "latency_s": round(time.monotonic() - start, 2),
        }
```

**Key adaptation notes for `filter.py`:**
- Function signature changes to `relevance_filter(items: list[RawItem], model: str) -> list[RawItem]`.
- Batch all items in one call (RESEARCH.md recommendation): build a numbered list of `title + summary` pairs as the user message.
- System prompt: use `RELEVANCE_SYSTEM_PROMPT` from RESEARCH.md Pattern 2 - copy verbatim.
- Parse JSON array response `[{"id": N, "verdict": "PASS"|"FAIL"}]` and return only items with verdict PASS.
- Replace `max_tokens: 512` with `max_tokens: 1024` for a batch of up to ~100 items (each JSON verdict is ~20 chars).
- Remove the `check_spend` / `total_cost_usd` global from the spike - not needed in production module.
- Add `"X-Title": "PersonalAgentHub/0.1"` to headers - drop "Spike" from the title.

---

### `src/agent_hub/db.py` (service, CRUD)

**No direct codebase analog** - the project has no SQLite layer yet.

**Pattern source:** RESEARCH.md Pattern 3 + Pattern 4 (SQLite schema and run ID generation).

**Schema constants to copy from RESEARCH.md:**
```python
CREATE_RAW_ITEMS = """
CREATE TABLE IF NOT EXISTS raw_items (
    id           TEXT PRIMARY KEY,
    run_id       TEXT NOT NULL,
    source_name  TEXT NOT NULL,
    title        TEXT NOT NULL,
    link         TEXT NOT NULL,
    published_at TEXT,
    summary      TEXT,
    ingested_at  TEXT NOT NULL
)
"""

CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    run_id         TEXT PRIMARY KEY,
    run_number     INTEGER NOT NULL,
    started_at     TEXT NOT NULL,
    completed_at   TEXT,
    status         TEXT,
    raw_count      INTEGER DEFAULT 0,
    relevant_count INTEGER DEFAULT 0,
    error_message  TEXT
)
"""
```

**Run ID generation pattern from RESEARCH.md Pattern 4:**
```python
def next_run_id(conn: sqlite3.Connection) -> tuple[int, str]:
    from datetime import date
    row = conn.execute("SELECT MAX(run_number) FROM runs").fetchone()
    n = (row[0] or 0) + 1
    date_str = date.today().isoformat()
    run_id = f"run-{n}-{date_str}"
    return n, run_id
```

**Security pattern - parameterized queries (RESEARCH.md Security Domain):**
```python
# Correct: always use ? placeholders - never f-string SQL
conn.execute(
    "INSERT INTO raw_items (id, run_id, source_name, title, link, published_at, summary, ingested_at) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    (item.id, item.run_id, item.source_name, item.title, item.link,
     item.published_at, item.summary, item.ingested_at)
)
```

**DB path:** `C:\Users\galzi\.microclaw\runtime\microclaw.db` - read from config, never hardcoded.

---

### `src/agent_hub/pipeline.py` (service, request-response)

**Analog:** `spikes/spike_watchlist.py` - orchestration shape in `main()` (lines 92-166)

**Orchestration pattern** (lines 99-106):
```python
all_results = []
all_items = []

for name, url in FEEDS.items():
    print(f"Fetching: {name}...")
    result = fetch_feed(name, url)
    all_results.append(result)
    all_items.extend(result["recent_entries"])
```

**Key adaptation notes for `pipeline.py`:**
- Replace the `for name, url in FEEDS.items()` loop with a loop over `config.load_sources()` filtering `enabled=True`.
- Wrap the loop in a try/except to record run failure in the `runs` table on exception.
- After `fetch_feed` loop: call `filter.relevance_filter(all_items, model)` → `relevant_items`.
- After filter: call `db.insert_raw_items(conn, relevant_items, run_id)` (only PASS items, per D-13).
- Before and after: call `db.start_run(conn)` / `db.complete_run(conn, status, counts)`.
- Final step: return a formatted Discord message string via `discord.format_success/failure/no_items`.
- The pipeline does NOT post to Discord directly - it returns the message string for MicroClaw to deliver.

---

### `src/agent_hub/discord.py` (utility, transform)

**No direct codebase analog** - message formatting is new.

**Pattern source:** RESEARCH.md Pattern 5 + CONTEXT.md D-08 exact formats.

**All three format helpers to copy verbatim from RESEARCH.md:**
```python
from datetime import datetime

def format_success(run_num: int, raw: int, relevant: int, sources: int, dt: datetime) -> str:
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return f"✅ Run #{run_num} - {ts}\n{raw} fetched → {relevant} relevant items from {sources} sources"

def format_failure(run_num: int, error: str, run_id: str, dt: datetime) -> str:
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return f"❌ Run #{run_num} failed - {ts}\n{error}\nRun ID: {run_id}"

def format_no_items(run_num: int, dt: datetime) -> str:
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return (
        f"⚠️ Run #{run_num} - {ts}\n"
        "0 relevant items (all sources returned no new AI content)"
    )
```

**Note:** These exact strings are user-confirmed in CONTEXT.md specifics. Do not alter the format characters (✅, ❌, ⚠️) or the `→` arrow in the success format.

---

### `tests/conftest.py` (test fixtures)

**Pattern source:** RESEARCH.md Code Examples section - fixture pattern to copy verbatim.

```python
import pytest

SAMPLE_RSS = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>GPT-5.5 released</title>
      <link>https://example.com/gpt55</link>
      <description>OpenAI releases GPT-5.5 with coding improvements.</description>
      <pubDate>Thu, 24 Apr 2026 12:00:00 +0000</pubDate>
    </item>
    <item>
      <title>How to use Codex (academy)</title>
      <link>https://openai.com/academy/codex</link>
      <description>Learn how to use Codex in 5 minutes.</description>
      <pubDate>Thu, 24 Apr 2026 11:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""

@pytest.fixture
def sample_rss():
    return SAMPLE_RSS

@pytest.fixture
def mock_openrouter_pass_response():
    return {"choices": [{"message": {"content": '[{"id":1,"verdict":"PASS"}]'}}], "usage": {"cost": 0.0}}

@pytest.fixture
def mock_openrouter_fail_response():
    return {"choices": [{"message": {"content": '[{"id":1,"verdict":"PASS"},{"id":2,"verdict":"FAIL"}]'}}], "usage": {"cost": 0.0}}
```

**Additional fixtures to add (not in RESEARCH.md, but required by test map):**
- `tmp_db_conn`: an in-memory `sqlite3.connect(":memory:")` connection with `init_db()` already called - used by `test_db.py` and `test_pipeline.py`.
- `sample_sources`: a list of two source dicts (one `enabled: true`, one `enabled: false`) for `test_ingester.py::test_disabled_sources_skipped`.

---

### `tests/test_ingester.py` (test, request-response)

**Analog:** `spikes/spike_watchlist.py` - tests mirror the `fetch_feed` function logic.

**Test coverage map from RESEARCH.md validation architecture:**
- `test_fetches_all_enabled_sources`: assert all `enabled: true` sources in `sample_sources` fixture are attempted (mock `httpx.Client.get`).
- `test_parses_rss_items`: feed `sample_rss` fixture through `feedparser.parse` path; assert returned `RawItem` list has correct fields.
- `test_date_fallback_chain`: construct entries with only `updated_parsed` set; assert `published_at` is populated.
- `test_disabled_sources_skipped`: assert sources with `enabled: false` are not fetched.

**Mock pattern for httpx** (standard pytest pattern; no codebase analog exists):
```python
from unittest.mock import patch, MagicMock

def test_parses_rss_items(sample_rss):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = sample_rss

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        items = fetch_feed("Test Feed", "https://example.com/rss")

    assert len(items) == 2
    assert items[0].title == "GPT-5.5 released"
```

---

### `tests/test_filter.py` (test, request-response)

**Analog:** `spikes/spike_openrouter.py` - tests mirror the `chat()` function's response parsing.

**Test coverage:**
- `test_relevance_filter_pass`: mock OpenRouter returning all-PASS verdict; assert all items returned.
- `test_relevance_filter_fail`: use `mock_openrouter_fail_response` fixture; assert only PASS items returned.
- `test_relevance_filter_empty`: pass empty list; assert empty list returned without making HTTP call.

**Mock pattern:** Use `unittest.mock.patch("httpx.post")` returning a `MagicMock` with `.json()` returning the fixture dict.

---

### `tests/test_db.py` (test, CRUD)

**No direct codebase analog.**

**Test coverage:**
- `test_run_id_format`: call `next_run_id(conn)` on empty DB; assert format matches `run-1-YYYY-MM-DD`.
- `test_insert_raw_item`: insert one `RawItem`; assert row count in `raw_items` table equals 1.
- `test_runs_crud`: start a run, complete it with `status="success"`; assert `runs` table has correct row.

**Uses `tmp_db_conn` fixture from conftest.py** (in-memory SQLite).

---

### `tests/test_discord.py` (test, transform)

**Pattern source:** RESEARCH.md Pattern 5 + CONTEXT.md D-08 exact formats.

**Test coverage (from RESEARCH.md validation architecture):**
- `test_format_success`: assert exact string match including `→` arrow and counts.
- `test_format_failure`: assert exact string including `Run ID:` line.
- `test_format_no_items`: assert exact string including `⚠️` and `0 relevant items` text.

**Example test:**
```python
from datetime import datetime
from src.agent_hub.discord import format_success

def test_format_success():
    dt = datetime(2026, 4, 25, 8, 1)
    result = format_success(run_num=42, raw=18, relevant=12, sources=7, dt=dt)
    assert result == "✅ Run #42 - 2026-04-25 08:01\n18 fetched → 12 relevant items from 7 sources"
```

---

### `tests/test_pipeline.py` (test, request-response)

**Analog:** `spikes/spike_watchlist.py` main() orchestration shape.

**Test coverage (from RESEARCH.md validation architecture):**
- `test_run_status_success`: mock `fetch_feed` returning 2 items, mock `relevance_filter` returning 1 PASS item; assert `runs` table shows `status="success"`, `raw_count=2`, `relevant_count=1`.
- `test_run_status_failure`: mock `relevance_filter` raising exception; assert `runs` table shows `status="failure"` with non-null `error_message`.

**Uses `tmp_db_conn` fixture; patches `fetch_feed` and `relevance_filter`.**

---

### `config/sources.yaml` (config)

**Analog:** `config/models.yaml` - YAML structure with top-level key wrapping a list.

**Existing models.yaml structure to mirror** (lines 1-13):
```yaml
# Per-task model selection. Each key independently tunable (D-15, D-17).
# Model IDs verified against OpenRouter /v1/models on 2026-04-25.
# Do not hardcode these IDs in application code -- always load from this file (D-17).
tasks:
  ranking:
    model: "google/gemini-3-flash-preview"
```

**sources.yaml structure (from RESEARCH.md Code Examples - copy verbatim):**
```yaml
# config/sources.yaml
# Source: D-01 through D-04 locked decisions, feed URLs from 00-03-SPIKE-RESULTS.md
sources:
  - name: "OpenAI Blog"
    url: "https://openai.com/blog/rss.xml"
    enabled: true
    note: "Mixes academy/tutorial content with news - relevance filter handles academy URLs"
  - name: "DeepMind Blog"
    url: "https://deepmind.google/blog/rss.xml"
    enabled: true
    note: "Low volume (~2/week), high signal"
  - name: "VS Code Blog"
    url: "https://code.visualstudio.com/feed.xml"
    enabled: true
    note: "Covers all VSCode changes, not just Copilot/AI - relevance filter needed"
  - name: "Ollama Releases"
    url: "https://github.com/ollama/ollama/releases.atom"
    enabled: true
    note: "High RC/patch noise - consider grouping in digest"
  - name: "TestingCatalog"
    url: "https://testingcatalog.com/feed/"
    enabled: true
    note: "High-signal brief AI product news"
  - name: "Simon Willison"
    url: "https://simonwillison.net/atom/everything/"
    enabled: true
    note: "High volume, includes minor links alongside real news"
  - name: "Latent Space"
    url: "https://www.latent.space/feed"
    enabled: true
    note: "Curated AINews daily roundups - highest value per item"
  - name: "Cursor Changelog"
    url: ""
    enabled: false
    note: "UNAVAILABLE - JS-rendered SPA, no RSS feed exists"
  - name: "Anthropic Blog"
    url: ""
    enabled: false
    note: "UNAVAILABLE - No RSS feed endpoint; all paths return 404"
```

---

### `config/models.yaml` (config - modify existing)

**Self-analog:** `config/models.yaml` lines 1-13.

**Existing content to preserve verbatim:**
```yaml
# Per-task model selection. Each key independently tunable (D-15, D-17).
# Model IDs verified against OpenRouter /v1/models on 2026-04-25.
# Do not hardcode these IDs in application code -- always load from this file (D-17).
tasks:
  ranking:
    model: "google/gemini-3-flash-preview"
  summarization:
    model: "nvidia/nemotron-3-super-120b-a12b"
  why_it_matters:
    model: "openai/gpt-5.4"
  embedding:
    model: "voyage-3"                        # UNVERIFIED: /v1/embeddings returning 401; verify API key billing before Phase 2
```

**Addition to append (D-06):**
```yaml
  relevance:
    model: "google/gemini-3-flash-preview"   # same as ranking per D-06
```

---

### `pyproject.toml` (config - new)

**No pyproject.toml exists in the repo.** Copy the exact block from RESEARCH.md Standard Stack section:

```toml
[project]
name = "agent-hub"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "feedparser==6.0.12",
    "httpx==0.28.1",
    "pyyaml==6.0.3",
    "pydantic>=2.13.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.3",
    "ruff>=0.15.12",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

---

## Shared Patterns

### Config Loading
**Source:** `spikes/spike_openrouter.py` lines 13-43
**Apply to:** `config.py`, any module that needs the OpenRouter key or model IDs
```python
# Canonical form - always use safe_load, always use Path(), always FileNotFoundError guard
from pathlib import Path
import yaml

with open(Path("config/models.yaml")) as f:
    models_cfg = yaml.safe_load(f)
MODELS = {k: v["model"] for k, v in models_cfg["tasks"].items()}
```

### OpenRouter HTTP Headers
**Source:** `spikes/spike_openrouter.py` lines 46-51
**Apply to:** `filter.py` (any module making OpenRouter calls)
```python
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "PersonalAgentHub/0.1",
}
```
Note: Change `X-Title` from the spike's `"Personal Agent Hub Spike"` to `"PersonalAgentHub/0.1"` for production.

### OpenRouter Response Parsing
**Source:** `spikes/spike_openrouter.py` lines 93-102
**Apply to:** `filter.py`
```python
data = resp.json()
choices = data.get("choices") or []
if not choices:
    raise ValueError(f"Empty choices in response: {data.get('error', data)}")
content = choices[0]["message"]["content"]
usage = data.get("usage", {})
cost = usage.get("cost", 0.0) or 0.0
```

### Error Handling in Service Functions
**Source:** `spikes/spike_watchlist.py` lines 86-89, `spikes/spike_openrouter.py` lines 111-116
**Apply to:** `ingester.py`, `filter.py`
```python
# Both spikes use the same pattern: broad except, return structured error dict
except Exception as e:
    result["status"] = "ERROR"
    result["error"] = str(e)
    return result
```
For production modules: replace the return-error-dict pattern with raising typed exceptions (`IngestionError`, `FilterError`) so `pipeline.py` can catch and record `status="failure"` in the runs table.

### Feed Fetch Safety (Anti-Pattern Guard)
**Source:** `spikes/spike_watchlist.py` lines 43-53
**Apply to:** `ingester.py`
```python
# CORRECT: httpx.get() then feedparser.parse(response.text)
with httpx.Client(follow_redirects=True, timeout=30.0) as client:
    response = client.get(url, headers=HEADERS)
feed = feedparser.parse(response.text)  # parse text, NOT the URL

# WRONG (never do this - loses user-agent control):
# feed = feedparser.parse(url)
```

### Parameterized SQLite Queries
**Source:** RESEARCH.md Security Domain
**Apply to:** `db.py` - all INSERT and SELECT statements
```python
# Always use ? placeholders - never f-string SQL
conn.execute("INSERT INTO raw_items (...) VALUES (?, ?, ...)", (val1, val2, ...))
```

---

## No Analog Found

Files with no close codebase match (planner should use RESEARCH.md patterns as the authoritative source):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/agent_hub/db.py` | service | CRUD | No SQLite layer exists in the codebase; no ORM or migration pattern to copy |
| `pyproject.toml` | config | - | No Python project structure exists yet; RESEARCH.md Standard Stack has the exact content |

---

## Metadata

**Analog search scope:** `/spikes/`, `/config/` (only directories with existing code)
**Files scanned:** 4 (spike_watchlist.py, spike_openrouter.py, models.yaml, microclaw.config.yaml)
**Pattern extraction date:** 2026-04-25
**Key constraint:** All 16 files are net-new (no `src/` or `tests/` directory exists). The two spike files are the entire codebase pattern corpus for Phase 1.
