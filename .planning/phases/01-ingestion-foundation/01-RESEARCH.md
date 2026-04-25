# Phase 1: Ingestion Foundation & Run Visibility - Research

**Researched:** 2026-04-25
**Domain:** Python/uv project bootstrap, RSS ingestion, SQLite schema, OpenRouter relevance filter, MicroClaw scheduling + Discord
**Confidence:** HIGH (all critical claims verified against live artifacts in this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Source Configuration**
- D-01: Feed URLs in `config/sources.yaml`. Consistent with D-19 (all YAML in one `config/` folder).
- D-02: Schema - each entry has `name`, `url`, `enabled` (bool), optional `note`.
- D-03: Start with 7 verified feeds from spike 00-03. Notes pre-populated for noisy sources.
- D-04: Cursor Changelog and Anthropic Blog documented as UNAVAILABLE (no RSS endpoint) in sources.yaml. Not active sources in Phase 1.

**Relevance Pre-Filter**
- D-05: Light AI-relevance pre-filter via OpenRouter on every daily run. Pass criteria: new model releases, AI coding tools, new AI tools, notable AI product updates, hot AI trends. Discard: tutorials/academy content, non-AI software releases, minor link posts unrelated to AI.
- D-06: New `relevance` task type added to `config/models.yaml`. Starter model: same as `ranking` (google/gemini-3-flash-preview). Config-driven - no hardcoded model IDs.
- D-07: Relevance check uses title + summary fields only (no extra HTTP fetch).

**Run Status Discord UX**
- D-08: Three distinct Discord message formats (success/failure/no-items). Exact formats confirmed.
- D-09: Run ID in every message. Format: `run-{N}-{YYYY-MM-DD}`.
- D-10: Success message shows both raw fetch count and post-filter relevant count.
- D-11: Plan 01-04's "3 separate Discord milestone posts" are dev-time run markers - bootstrap, ingestion, schedule registration. Not the same as daily run-status messages.

**Raw Item SQLite Schema**
- D-12: `raw_items` table - 8 fields: `id`, `run_id`, `source_name`, `title`, `link`, `published_at`, `summary`, `ingested_at`.
- D-13: Phase 1 stores only items that PASS the relevance filter. No rejected table in Phase 1.
- D-14: `runs` table - `run_id`, `run_number`, `started_at`, `completed_at`, `status`, `raw_count`, `relevant_count`, `error_message`.

**Schedule & Runtime**
- D-15: Daily run at 08:00 local Windows time via MicroClaw scheduler.
- D-16: Phase 1 is outbound-only. No inbound user flows.

### Claude's Discretion
- SQLite schema migrations approach (direct CREATE TABLE or lightweight migration)
- Retry/timeout defaults for the httpx feed fetch calls
- Relevance filter prompt design (few-shot examples vs zero-shot)
- Batch vs per-item OpenRouter calls for the relevance filter
- Test fixture strategy for Phase 1 test harness

### Deferred Ideas (OUT OF SCOPE)
- Per-source filtering rules beyond human-readable `note`
- Control panel model-selection UI
- DM-based bot-receiver flow
- `rejected_items` table
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SRC-01 | User receives candidate updates gathered from a curated multi-source watchlist rather than a single feed. | 7 verified feed URLs from spike 00-03; feedparser+httpx pattern confirmed; `config/sources.yaml` schema defined in D-01/D-02. |
| DGST-04 | User can see whether the daily digest run completed, failed, or produced no qualifying items. | Three Discord message formats defined in D-08; `runs` table schema in D-14; MicroClaw scheduler confirmed working in spike 00-01. |
</phase_requirements>

---

## Summary

Phase 1 builds on fully validated Phase 0 infrastructure. MicroClaw is confirmed working on Windows 11 (Plan 00-01 GO). Seven RSS/Atom feeds are verified and URLs corrected (Plan 00-03 GO). The OpenRouter API key placeholder (`sk-ore-AAABBBCCC`) in `config/microclaw.config.yaml` is the critical unresolved item - Plan 01-04 must substitute a real key before the live runtime can be proven. All Phase 0 spike code (`spike_watchlist.py`, `spike_openrouter.py`) is directly reusable as the pattern basis for production ingestion and relevance filter code.

The repository has no Python project structure yet - no `pyproject.toml`, no `src/` layout, no test directory. Plan 01-01 must bootstrap uv + pytest from scratch. uv 0.8.13 is installed and Python 3.12.11 is available as a managed uv Python. The primary technical challenge in Phase 1 is not any novel technology but wiring together already-validated pieces: the feed-fetch pattern, the OpenRouter HTTP client pattern, the MicroClaw scheduler `once`-type task for daily scheduling, and the Discord post format.

The MicroClaw `scheduled_tasks` table schema confirms scheduling uses `chat_id`, `prompt`, `schedule_type`, and `schedule_value` fields. The only confirmed `schedule_type` in the live DB is `once` (from the spike). The 08:00 recurring daily trigger will require the correct `schedule_type` value - either a `cron`/`daily`/`recurring` type that MicroClaw supports but was not exercised in the spike, or re-registering a `once` task after each run. This is the primary unknown that Plan 01-04 must resolve via MicroClaw documentation or experimentation.

**Primary recommendation:** Bootstrap uv/pytest in Plan 01-01 using a minimal `pyproject.toml` with Python 3.12 pin, adapt the spike code into `src/agent_hub/` modules in Plan 01-02, add run-state in Plan 01-03, and wire the live MicroClaw + OpenRouter integration in Plan 01-04. Keep all MicroClaw interaction as natural-language prompts fired into a dedicated chat - do not try to call MicroClaw APIs directly.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| RSS feed fetching | Python sidecar | - | Pure HTTP + parse; no MicroClaw involvement needed |
| Relevance pre-filter (OpenRouter) | Python sidecar | - | Direct httpx call to OpenRouter; sidecar owns the prompt |
| SQLite persistence (raw_items, runs) | Python sidecar | - | Sidecar writes directly to shared microclaw.db at the same path |
| Run orchestration (start/end/status) | Python sidecar | - | Sidecar owns the run state machine; updates `runs` table |
| Discord status message | MicroClaw | Python sidecar triggers | MicroClaw's Discord adapter sends; sidecar provides the formatted text via MicroClaw prompt |
| 08:00 daily schedule trigger | MicroClaw scheduler | - | MicroClaw scheduler fires the daily prompt; Python sidecar executes the actual pipeline |
| `config/sources.yaml` loading | Python sidecar | - | YAML file read at startup; no MicroClaw involvement |
| `config/models.yaml` loading | Python sidecar | - | Same pattern as established in spike_openrouter.py |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.11 | Runtime for all ingestion and filter logic | Available as managed uv Python; confirmed in this session [VERIFIED: uv python list] |
| uv | 0.8.13 | Project/env/package management | Installed on this machine; faster than pip for green-field Python [VERIFIED: uv --version] |
| feedparser | 6.0.12 | RSS/Atom parsing | Latest stable; used successfully in spike_watchlist.py [VERIFIED: pip index versions] |
| httpx | 0.28.1 | HTTP client for feeds and OpenRouter | Already installed; proven pattern in both spike files [VERIFIED: pip show httpx] |
| PyYAML | 6.0.3 | Load config/sources.yaml and config/models.yaml | Latest stable; standard safe_load pattern [VERIFIED: pip index versions] |
| pydantic | 2.13.3 | Typed schema for RawItem, RunRecord | Latest stable [VERIFIED: pip index versions] |
| pytest | 9.0.3 | Test harness for fixture-backed SRC-01 tests | Latest stable; used in existing miniconda env [VERIFIED: pip index versions] |

### Supporting (Dev)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ruff | 0.15.12 | Linting + formatting | All Python files; `ruff check` + `ruff format` [VERIFIED: pip index versions] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML | ruamel.yaml | ruamel.yaml preserves comments; unnecessary for Phase 1 machine-read only |
| pydantic | dataclasses | pydantic adds validation and `.model_dump()` for free; worth it for pipeline boundaries |
| pytest fixtures | pytest-recording / VCR | VCR is more powerful for HTTP replay but over-engineered; simple fixtures sufficient for Phase 1 |

**Installation (pyproject.toml `[project.dependencies]`):**
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
```

**Bootstrap command:**
```bash
uv init --python 3.12 --name agent-hub
uv add feedparser==6.0.12 httpx==0.28.1 pyyaml==6.0.3 "pydantic>=2.13.3"
uv add --dev "pytest>=9.0.3" "ruff>=0.15.12"
```

---

## Architecture Patterns

### System Architecture Diagram

```
[MicroClaw scheduler: 08:00 cron/daily]
         |
         | fires prompt into dedicated daily-digest chat
         v
[MicroClaw agent loop]
         |
         | executes Python sidecar via bash tool
         v
[src/agent_hub/pipeline.py: run orchestrator]
    |          |           |
    v          v           v
[ingester]  [filter]   [run_record]
    |          |           |
    | httpx    | httpx      | sqlite3
    v          v           v
[7 RSS feeds] [OpenRouter] [microclaw.db]
              relevance     raw_items +
              /v1/chat       runs tables
                   |
                   v
         [Discord status message]
         via MicroClaw prompt
         (success/failure/no_items format)
```

### Recommended Project Structure

```
src/
├── agent_hub/
│   ├── __init__.py
│   ├── config.py        # YAML loaders for sources.yaml and models.yaml
│   ├── ingester.py      # fetch_feed() - httpx + feedparser pattern from spike
│   ├── filter.py        # relevance_filter() - OpenRouter chat call
│   ├── db.py            # SQLite init, raw_items insert, runs CRUD
│   ├── pipeline.py      # run_digest() - orchestrates ingest → filter → persist → notify
│   └── discord.py       # format_run_message() - D-08 format helpers
tests/
├── conftest.py          # shared fixtures (sample feed XML, mock OpenRouter responses)
├── test_ingester.py     # SRC-01 fixture-backed tests
├── test_filter.py       # relevance filter unit tests with mock responses
├── test_db.py           # raw_items and runs table tests
└── test_pipeline.py     # end-to-end pipeline smoke test
config/
├── sources.yaml         # 7 verified feed URLs (D-01 through D-04)
└── models.yaml          # per-task model selection (adds `relevance` key in Phase 1)
pyproject.toml           # uv-managed project
```

### Pattern 1: Feed Fetch (from spike_watchlist.py - copy/adapt)

**What:** `httpx.get()` then `feedparser.parse(response.text)` - never call feedparser with a URL directly (no user-agent control).

**When to use:** Every feed in sources.yaml.

```python
# Source: spikes/spike_watchlist.py (verified working, 2026-04-25)
from time import mktime
from datetime import datetime, timezone

HEADERS = {"User-Agent": "PersonalAgentHub/0.1"}

def fetch_feed(name: str, url: str) -> list[dict]:
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        response = client.get(url, headers=HEADERS)
    response.raise_for_status()
    feed = feedparser.parse(response.text)
    items = []
    for entry in feed.entries:
        published = None
        for field in ["published_parsed", "updated_parsed", "created_parsed"]:
            parsed = entry.get(field)
            if parsed:
                published = datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
                break
        items.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published_at": published.isoformat() if published else None,
            "summary": entry.get("summary", ""),
        })
    return items
```

### Pattern 2: OpenRouter Relevance Filter (adapt from spike_openrouter.py)

**What:** POST to `/v1/chat/completions` with a batch of title+summary pairs. Returns pass/fail per item.

**When to use:** After ingestion, before SQLite storage (D-13: only PASS items stored).

**Batch vs per-item decision (Claude's Discretion):**
- Batch all items in one call: ~50-100 tokens per item input + a single system prompt overhead (~200 tokens). For 78 items at $0.15/1M input tokens (Gemini Flash), a batch call costs roughly $0.002. One API call vs 78 calls.
- Per-item calls: simpler code, easier retry logic, higher latency. At 78 items, adds ~10-30s total.
- **Recommendation: batch all items in a single call** with a JSON-structured response listing pass/fail per item ID. Simpler retry (one failure = one retry), lower cost, faster.

**Prompt design (few-shot recommended over zero-shot):**

```python
# Source: adapted from spikes/spike_openrouter.py pattern (verified, 2026-04-25)
RELEVANCE_SYSTEM_PROMPT = """
You are a relevance classifier for an AI news digest.
For each item, output PASS or FAIL.

PASS if the item is about:
- New model releases or major model updates
- AI coding tools (Cursor, Copilot, Codex, etc.)
- New AI tools or notable AI product launches
- Hot AI trends or research breakthroughs

FAIL if the item is:
- Tutorial or academy/educational content
- Non-AI software releases
- Minor link posts or social reactions unrelated to AI products
- RC patches or minor version bumps (e.g. Ollama v0.21.3-rc0)

Respond with a JSON array: [{"id": 1, "verdict": "PASS"}, ...]
""".strip()
```

**Few-shot note:** Including 2-3 examples in the system prompt (one clear PASS, one clear FAIL, one ambiguous-but-FAIL for academy content) improves accuracy for the OpenAI academy-content problem observed in the spike data. [ASSUMED - based on general LLM prompting practice; not benchmarked on this specific model]

### Pattern 3: SQLite Schema Init (no migration framework needed)

**What:** Direct `CREATE TABLE IF NOT EXISTS` at startup. MicroClaw owns its own schema via its `schema_migrations` table (20 migrations applied). Phase 1 app tables are application-owned, not MicroClaw-owned.

**When to use:** Once at startup in `db.py`; idempotent.

```python
# Source: inferred from D-12/D-14 schema decisions + live DB inspection (2026-04-25)
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

**Migration rationale:** A lightweight migration approach (version counter in a separate `app_schema_version` table) is worth adding even in Phase 1, since Phase 2 will add new columns. However, given Phase 1 is greenfield and the DB is empty for our app tables, `CREATE TABLE IF NOT EXISTS` is sufficient for now. [ASSUMED - complexity estimate; user may prefer alembic if Phase 2 adds heavy schema changes]

### Pattern 4: Run ID Generation

**What:** Sequential run number from the `runs` table + date suffix.

```python
# Source: D-09 format + D-14 schema
def next_run_id(conn: sqlite3.Connection) -> tuple[int, str]:
    from datetime import date
    row = conn.execute("SELECT MAX(run_number) FROM runs").fetchone()
    n = (row[0] or 0) + 1
    date_str = date.today().isoformat()
    run_id = f"run-{n}-{date_str}"
    return n, run_id
```

### Pattern 5: Discord Status Message Formatting (D-08)

```python
# Source: D-08 exact formats confirmed by user in CONTEXT.md specifics section
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

### Pattern 6: MicroClaw Scheduler Registration

**What:** The MicroClaw scheduler is triggered via a Discord @-mention prompt (F1 contract). The scheduler fires a natural-language instruction into a designated chat. For the daily 08:00 task, a `cron` or `daily` schedule_type is needed.

**What we know from the live DB:**
- `scheduled_tasks` columns: `id`, `chat_id`, `prompt`, `schedule_type`, `schedule_value`, `timezone`, `next_run`, `last_run`, `status`, `created_at` [VERIFIED: PRAGMA table_info on live DB]
- Only observed `schedule_type` value: `once` (from the spike test) [VERIFIED: live DB query]
- The recurring daily schedule requires a different `schedule_type` value - candidate values: `daily`, `cron`, or `recurring` [ASSUMED - not observed in spike; must be confirmed via MicroClaw docs or experimentation in Plan 01-04]

**Recommended approach for Plan 01-04:**
Register the 08:00 schedule via an @-mention prompt in natural language (e.g., `@Personal Agent Hub schedule the daily digest run every day at 08:00`). MicroClaw's LLM will parse this and write the appropriate `schedule_type`/`schedule_value` into the `scheduled_tasks` table. Verify the inserted row after registration to confirm the schedule_type value.

**Fallback:** If MicroClaw does not support recurring `daily` or `cron` schedules, use Windows Task Scheduler to fire `microclaw --config ./config/microclaw.config.yaml` with a specific prompt at 08:00. [ASSUMED - fallback validity not verified]

### Anti-Patterns to Avoid

- **Calling `feedparser.parse(url)` directly:** Loses user-agent control and may trigger bot-blocking. Always use `httpx.get()` first, then `feedparser.parse(response.text)`.
- **Hardcoding model IDs in Python source:** D-17 regression. Always read from `config/models.yaml`.
- **Writing to microclaw.db before calling `CREATE TABLE IF NOT EXISTS`:** Phase 1 tables don't exist yet (confirmed by DB inspection). Any code that assumes the table exists will fail.
- **Storing all fetched items before relevance filter:** D-13 says store only PASS items. Fetching everything then filtering in SQLite wastes storage and complicates future queries.
- **Making the Discord post itself from Python:** The correct pattern is to instruct MicroClaw to post (via a prompt containing the pre-formatted message). MicroClaw's Discord adapter handles delivery.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS parsing | Custom XML parser | feedparser 6.0.12 | Handles malformed XML, CDATA, encoding variants, both RSS and Atom transparently |
| HTTP feed fetch | Requests + manual redirect | httpx with `follow_redirects=True` | Connection pooling, timeout, redirect handling, modern TLS already built in |
| YAML config loading | String parsing | PyYAML `safe_load()` | Handles multi-line, anchors, edge cases; `safe_load` avoids arbitrary object execution |
| Typed item schema | Raw dicts | pydantic BaseModel | Free validation, `.model_dump()`, IDE completion, pipeline boundary contracts |
| Date-field fallback chain | Custom logic | The 3-field chain from spike | Already battle-tested against all 7 feeds in the backtest |

---

## Common Pitfalls

### Pitfall 1: MicroClaw scheduler `schedule_type` unknown for recurring daily runs

**What goes wrong:** Plan 01-04 registers the 08:00 schedule, but uses the wrong `schedule_type` string and the task never fires, or fires as `once` and stops after day 1.

**Why it happens:** Spike 00-01 only tested `once` scheduling. The recurring daily type was not exercised.

**How to avoid:** In Plan 01-04, after registering the schedule via @-mention, immediately inspect the `scheduled_tasks` row with a DB query to verify `schedule_type` and `schedule_value` values. If `schedule_type` is `once`, the scheduler may not support true recurring tasks - escalate to Windows Task Scheduler fallback.

**Warning signs:** Task shows `status = 'completed'` after first run but no subsequent `next_run` value is set.

### Pitfall 2: OpenRouter API key placeholder blocks live runtime

**What goes wrong:** `config/microclaw.config.yaml` has `openrouter_api_key: "sk-ore-AAABBBCCC"` (confirmed placeholder). All OpenRouter calls in Plan 01-04 will return 401.

**Why it happens:** Phase 0 spike ran with the placeholder key and failed with 401 (confirmed in `spikes/openrouter_eval_output.txt`). The real key was never substituted.

**How to avoid:** Plan 01-04 must have an explicit task: "Replace `openrouter_api_key` in `config/microclaw.config.yaml` with the real OpenRouter API key." This is a human step, not automated.

**Warning signs:** Any OpenRouter call returns 401 with `{"error":{"message":"Missing Authentication header","code":401}}`.

### Pitfall 3: `raw_items` and `runs` tables absent until explicitly created

**What goes wrong:** Code imports `db.py` and tries to insert a run record, but the tables don't exist yet in `microclaw.db`.

**Why it happens:** Phase 1 tables are not part of MicroClaw's built-in schema (confirmed by DB inspection - 26 MicroClaw tables, neither `raw_items` nor `runs` present).

**How to avoid:** Call `init_db(conn)` which runs both `CREATE TABLE IF NOT EXISTS` statements before any pipeline code writes to the DB. Make this the first call in `pipeline.py`.

**Warning signs:** `sqlite3.OperationalError: no such table: raw_items`

### Pitfall 4: OpenAI Blog mixes academy/tutorial content with real news

**What goes wrong:** The relevance filter passes OpenAI academy items (e.g., "Working with Codex", "Codex Settings") because titles look AI-adjacent.

**Why it happens:** The OpenAI Blog RSS mixes launch announcements with `openai.com/academy/` tutorials in the same feed - observed directly in the 00-03 backtest (7 of 18 OpenAI items were academy content).

**How to avoid:** Include an explicit example in the relevance filter prompt: academy/tutorial titles from `openai.com/academy/` should always be FAIL. Alternatively, a URL-based pre-check (`if '/academy/' in link → skip before LLM call`) is a cheap zero-cost guard.

**Warning signs:** Success message shows high raw count but relevant count is still high; manual review shows tutorial items in `raw_items`.

### Pitfall 5: Ollama RC/patch noise clutters the digest

**What goes wrong:** Ollama Releases feed has ~7 items/week (confirmed in backtest), many of which are RC or patch noise (v0.21.2-rc0, v0.21.2-rc1, v0.21.1-rc1, v0.21.3-rc0). The relevance filter's "minor version bumps" FAIL rule handles this - but the rule must be explicit.

**Why it happens:** The relevance filter default behavior is to PASS items that look AI-tool-adjacent. RC releases of Ollama look like AI tool updates.

**How to avoid:** Explicitly include "minor version bumps, RC releases, and patch-only releases" in the FAIL examples in the relevance prompt. The `note` field in `sources.yaml` for Ollama already documents this: "High RC/patch noise."

### Pitfall 6: `microclaw.config.yaml` in repo root (not `config/`) at plan execution time

**What goes wrong:** D-19 specifies `config/microclaw.config.yaml`, but the repo currently has `./microclaw.config.yaml` at root. Phase 1 code referencing `config/microclaw.config.yaml` will fail with FileNotFoundError.

**Why it happens:** Relocation from root to `config/` was deferred in Phase 0 CONTEXT.md (Deferred Ideas). The file still sits at repo root as of 2026-04-25 (confirmed by `ls` output).

**How to avoid:** Plan 01-01 must include an explicit task to move `microclaw.config.yaml` → `config/microclaw.config.yaml` and update `.gitignore` accordingly. Also update `microclaw --config` argument if MicroClaw references the config by explicit path.

**Warning signs:** `FileNotFoundError: config/microclaw.config.yaml` when running any code that loads config from the expected path.

---

## Code Examples

### sources.yaml Schema (D-01/D-02/D-03/D-04)

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

### models.yaml addition (D-06)

```yaml
# config/models.yaml - add `relevance` task (D-06)
tasks:
  ranking:
    model: "google/gemini-3-flash-preview"
  summarization:
    model: "nvidia/nemotron-3-super-120b-a12b"
  why_it_matters:
    model: "openai/gpt-5.4"
  embedding:
    model: "voyage-3"
  relevance:
    model: "google/gemini-3-flash-preview"   # same as ranking per D-06
```

### Fixture pattern for SRC-01 tests

```python
# tests/conftest.py
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

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Local Ollama for LLM | OpenRouter remote-only | 2026-04-24 (D-13) | All LLM calls go to OpenRouter; local Python never talks to Ollama |
| `microclaw.config.yaml` at repo root | `config/microclaw.config.yaml` | Deferred to Phase 1 (D-19) | Phase 1 code must reference the new path; relocation is a Plan 01-01 task |
| No `relevance` task in models.yaml | `relevance` task added (D-06) | Phase 1 | Phase 1 adds the fifth task key to models.yaml |

**Deprecated/outdated:**
- `microclaw.config.yaml` at repo root: superseded by D-19; relocation is a Phase 1 setup step.
- Any spike code that references the config at repo root: `spike_openrouter.py` already uses `config/microclaw.config.yaml` correctly (confirmed in code). Root-level file is a legacy artifact.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | MicroClaw supports a recurring `daily` or `cron` schedule_type for the 08:00 task | Architectural Responsibility Map, Pattern 6, Pitfall 1 | If only `once` is supported, Plan 01-04 must fall back to Windows Task Scheduler - additional setup complexity |
| A2 | Few-shot examples in the relevance prompt improve accuracy over zero-shot for the academy-content problem | Pattern 2, Pitfall 4 | Zero-shot may be sufficient; few-shot adds ~100 tokens to the system prompt (~$0.00002/run - negligible cost risk) |
| A3 | `CREATE TABLE IF NOT EXISTS` is sufficient for Phase 1 without a migration framework | Pattern 3 | If Phase 2 adds columns, an ALTER TABLE or migration tool will be needed; not a Phase 1 blocker |
| A4 | Windows Task Scheduler is a viable fallback if MicroClaw does not support recurring schedules | Pattern 6 | Fallback untested; may have its own Windows-specific quirks |
| A5 | The OpenRouter API key needs to be substituted manually by the user in Plan 01-04 | Pitfall 2 | If the user already has a real key inserted elsewhere, this is a no-op - but the current file value is confirmed as a placeholder |

---

## Open Questions

1. **MicroClaw recurring schedule_type value**
   - What we know: Live DB shows `schedule_type = 'once'` for the spike task. `schedule_value` for that task was an ISO datetime string.
   - What's unclear: Whether MicroClaw supports a `daily` or `cron` schedule_type for recurring tasks, and what the `schedule_value` format is (cron expression? time string?).
   - Recommendation: Plan 01-04 first task: send `@Personal Agent Hub what schedule types are supported for recurring daily tasks?` to the MicroClaw bot, inspect the `scheduled_tasks` row after a test registration.

2. **How MicroClaw fires the Python sidecar**
   - What we know: MicroClaw has bash tool execution (`sandbox.mode = off` in config). The agent can run Python scripts via bash.
   - What's unclear: The exact prompt structure for the daily task trigger - does it call `uv run python -m agent_hub.pipeline`? Does it expect a specific script path?
   - Recommendation: Plan 01-04 defines the exact prompt string that MicroClaw will execute as part of the scheduled task registration. Keep it as a `uv run` invocation with an absolute path to the script.

3. **Sources.yaml - does Phase 1 add a `config/` path to `.gitignore` or track sources.yaml as safe?**
   - What we know: `.gitignore` currently has `config/microclaw.config.yaml` gitignored explicitly; `!config/models.yaml` is tracked. No entry yet for `config/sources.yaml`.
   - What's unclear: `sources.yaml` contains no secrets (just URLs) so it should be tracked. Plan 01-01 must verify the gitignore is correct.
   - Recommendation: Add `config/sources.yaml` to git explicitly (it has no secrets). The existing `!config/models.yaml` pattern is the precedent.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | Python env management | ✓ | 0.8.13 | pip + venv (slower) |
| Python 3.12 | Runtime | ✓ | 3.12.11 (uv managed) | Python 3.13.12 (also available) |
| feedparser | RSS parsing | ✓ (pip env, not uv venv yet) | 6.0.12 | - |
| httpx | HTTP client | ✓ | 0.28.1 | - |
| pydantic | Schema validation | ✓ | 2.12.4 (2.13.3 latest) | - |
| pytest | Test harness | ✓ | 9.0.2 (9.0.3 latest) | - |
| MicroClaw | Agent runtime + Discord | ✓ | v0.1.50 (validated 2026-04-23) | - |
| microclaw.db | SQLite runtime DB | ✓ | 284KB, 26 tables, at `C:\Users\galzi\.microclaw\runtime\microclaw.db` | - |
| OpenRouter API key | LLM relevance filter | ✗ (placeholder only) | - | Human must substitute real key in config/microclaw.config.yaml |

**Missing dependencies with no fallback:**
- Real OpenRouter API key - blocks Plan 01-04 live runtime test. Must be manually substituted by user.

**Missing dependencies with fallback:**
- None beyond the API key.

**Note:** feedparser, httpx, pydantic, pytest are currently installed in a miniconda/pip environment (not in a uv-managed project venv). Plan 01-01 creates the uv venv and installs them fresh there. No conflicts expected.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` - Wave 0 creates this |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SRC-01 | All 7 enabled feeds in sources.yaml are attempted during a run | unit | `uv run pytest tests/test_ingester.py::test_fetches_all_enabled_sources -x` | Wave 0 |
| SRC-01 | Items from a fixture-backed feed are parsed into RawItem schema | unit | `uv run pytest tests/test_ingester.py::test_parses_rss_items -x` | Wave 0 |
| SRC-01 | Date fallback chain (published_parsed → updated_parsed → created_parsed) works | unit | `uv run pytest tests/test_ingester.py::test_date_fallback_chain -x` | Wave 0 |
| SRC-01 | Disabled sources in sources.yaml are skipped | unit | `uv run pytest tests/test_ingester.py::test_disabled_sources_skipped -x` | Wave 0 |
| DGST-04 | Success Discord message format matches D-08 spec exactly | unit | `uv run pytest tests/test_discord.py::test_format_success -x` | Wave 0 |
| DGST-04 | Failure Discord message format matches D-08 spec exactly | unit | `uv run pytest tests/test_discord.py::test_format_failure -x` | Wave 0 |
| DGST-04 | No-items Discord message format matches D-08 spec exactly | unit | `uv run pytest tests/test_discord.py::test_format_no_items -x` | Wave 0 |
| DGST-04 | Run ID format matches `run-{N}-{YYYY-MM-DD}` pattern | unit | `uv run pytest tests/test_db.py::test_run_id_format -x` | Wave 0 |
| DGST-04 | `runs` table records status=success on clean pipeline run | integration | `uv run pytest tests/test_pipeline.py::test_run_status_success -x` | Wave 0 |
| DGST-04 | `runs` table records status=failure on OpenRouter error | integration | `uv run pytest tests/test_pipeline.py::test_run_status_failure -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x -q`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/conftest.py` - shared fixtures (SAMPLE_RSS, mock_openrouter_pass/fail responses, tmp SQLite connection)
- [ ] `tests/test_ingester.py` - covers SRC-01 ingestion tests
- [ ] `tests/test_filter.py` - covers relevance filter with mocked OpenRouter responses
- [ ] `tests/test_db.py` - covers raw_items insert, runs CRUD, run_id generation
- [ ] `tests/test_discord.py` - covers D-08 format helpers
- [ ] `tests/test_pipeline.py` - covers end-to-end smoke (all mocked except SQLite)
- [ ] `pyproject.toml` - uv project with pytest config and dependencies
- [ ] Framework install: `uv add feedparser==6.0.12 httpx==0.28.1 pyyaml==6.0.3 "pydantic>=2.13.3"` + dev deps

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Phase 1 is outbound-only; no user auth |
| V3 Session Management | No | No sessions in Phase 1 |
| V4 Access Control | No | Single-user local system |
| V5 Input Validation | Yes | pydantic validates RawItem fields; feedparser input is untrusted RSS XML |
| V6 Cryptography | No | No crypto needed; secrets stored in gitignored YAML file |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Feed URL injecting malicious content into summary/title fields | Tampering | pydantic field validators; do not eval/exec any feed content; treat all RSS fields as untrusted strings |
| SQLite injection via unsanitized title/link fields | Tampering | Use parameterized queries (`?` placeholders) in all `db.py` inserts - never f-string SQL |
| OpenRouter API key exposure via logs | Information Disclosure | Never log the API key; load from file; config/microclaw.config.yaml is gitignored |
| Bot token in microclaw.config.yaml committed accidentally | Information Disclosure | .gitignore entry confirmed for config/microclaw.config.yaml; verify after relocation in Plan 01-01 |

---

## Sources

### Primary (HIGH confidence - verified in this session)

- Live microclaw.db inspection - `scheduled_tasks` schema, existing tables, confirmed Phase 1 tables absent
- `spikes/spike_watchlist.py` - confirmed feed fetch pattern + date fallback chain
- `spikes/spike_openrouter.py` - confirmed OpenRouter httpx client pattern
- `config/models.yaml` - confirmed existing task keys, verified Gemini Flash model ID
- `config/microclaw.config.yaml` - confirmed placeholder API key `sk-ore-AAABBBCCC`
- `.planning/phases/00-validation-spikes/00-03-SPIKE-RESULTS.md` - confirmed 7 feed URLs, volume data
- `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md` - confirmed MicroClaw scheduler `once` contract
- `spikes/openrouter_eval_output.txt` - confirmed 401 failure with placeholder key
- `uv python list` + `pip index versions` - confirmed Python 3.12.11, package latest versions

### Secondary (MEDIUM confidence)

- `.planning/research/STACK.md` - project stack recommendations (some Ollama entries outdated per D-13)
- `.planning/research/ARCHITECTURE.md` - system architecture overview
- Phase 0 CONTEXT.md decisions D-01 through D-24

### Tertiary (LOW confidence)

- Assumption A1 (MicroClaw recurring schedule_type) - behavioral extrapolation, not verified in docs or DB

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all versions verified against pip registry and live installs
- Feed ingestion pattern: HIGH - verified in spike_watchlist.py against all 7 feeds
- OpenRouter client pattern: HIGH - code verified in spike_openrouter.py; 401 failure from placeholder key understood
- SQLite schema: HIGH - live DB inspected; Phase 1 tables confirmed absent
- MicroClaw scheduling: MEDIUM - `once` type confirmed; recurring type assumed (A1)
- Relevance filter prompt design: MEDIUM - pattern from spike code; few-shot recommendation is ASSUMED

**Research date:** 2026-04-25
**Valid until:** 2026-05-25 (stable stack; MicroClaw version unlikely to change within 30 days)
