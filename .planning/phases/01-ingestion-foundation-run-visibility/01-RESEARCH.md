# Phase 1: Ingestion Foundation & Run Visibility - Research

**Researched:** 2026-04-11 [VERIFIED: session date]  
**Domain:** Local-first feed ingestion, run orchestration, and Discord-visible run tracing on MicroClaw [CITED: .planning/ROADMAP.md]  
**Confidence:** MEDIUM-HIGH [ASSUMED]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Source watchlist shape
- **D-01:** Phase 1 intake uses official product sources plus a small curated industry layer, not official-only intake and not a broad community/social sweep. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-02:** Start with a small, high-trust seed watchlist that can expand later rather than trying to launch with broad coverage. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-03:** The non-official layer should mostly be high-signal AI news and product trackers, with only a tiny allowlist of proven trend-watchers. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-04:** Sources without a clean feed or API are skipped in Phase 1 unless they later become important enough to justify a fallback path. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-05:** The starter watchlist is managed through a simple local config/allowlist, not through Discord commands or a control-panel editing UI. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-06:** The watchlist enforces trust tiers: official sources highest, curated trackers next, trend-watchers lowest. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-07:** Official blogs/changelogs and GitHub release feeds must be included in the starter watchlist. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

#### Run visibility in Discord
- **D-08:** Run-status messages live in a dedicated shared agent-status side channel; the digest channel stays clear and focused on the delivered digest. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-09:** Discord-visible narration should cover only major milestones: run start, ingestion complete, and final outcome. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-10:** Successful runs should post a concise summary with key counts and a link back to the deeper trace. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-11:** Failed runs and no-qualifying-item runs should both post explicit status messages with a short reason and a trace link. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

#### Run trace details
- **D-12:** Each visible run uses a human-readable label with date/time plus a short run ID, not timestamp-only or opaque internal identifiers. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-13:** Status-message trace links should land on the exact run's raw event/log view. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-14:** The default trace surface is an append-only event timeline with timestamps, event types, and outcome markers. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-15:** Every retry or manual rerun gets its own run label and short ID, with links between related runs rather than overwriting a day-level identity. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

#### Schedule and rerun behavior
- **D-16:** The scheduled digest run executes every day at **08:00 local time**. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-17:** Manual on-demand reruns are allowed and must be clearly labeled as separate runs. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **D-18:** A scheduled failure gets one automatic retry after a short delay; if it still fails, the failure is surfaced clearly. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

### the agent's Discretion
- Exact starter source names within the chosen trust tiers and source types. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- Exact local config file shape and storage location for the Phase 1 watchlist. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- Exact short run ID format and human-readable naming convention. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- Exact event schema fields and UI presentation details within the append-only timeline model. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- Exact delay before the single automatic retry. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

### Deferred Ideas (OUT OF SCOPE)
- **Rescope v1 around one visible workflow** — Reviewed but not folded because the current roadmap and Phase 1 boundary already assume one visible workflow; it does not add extra implementation scope to this phase. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

No additional deferred feature ideas surfaced during discussion. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SRC-01 | User receives candidate updates gathered from a curated multi-source watchlist rather than a single feed. [CITED: .planning/REQUIREMENTS.md] | Starter trust-tier watchlist, local watchlist config, RSS/API-first connectors, raw item persistence, and source-level validation strategy. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| DGST-04 | User can see whether the daily digest run completed, failed, or produced no qualifying items. [CITED: .planning/REQUIREMENTS.md] | Run lifecycle model, append-only event timeline, Discord side-channel milestone messages, exact-run trace links, retry/rerun lineage, and validation test map. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
</phase_requirements>

## Summary

Phase 1 should be planned as one explicit MicroClaw-driven workflow with four bounded concerns: source watchlist config, feed/API ingestion, run/event persistence, and Discord-visible status narration. That matches the project direction toward a workflow-oriented local monolith, not a worker mesh. [CITED: .planning/research/ARCHITECTURE.md] [CITED: .planning/notes/visible-routing-architecture.md]

The planning risk is not ingestion volume; it is trust and traceability. The first implementation must prove that a daily run can ingest from several named sources, persist raw intake, emit a run-scoped event trail, and surface a final outcome tied to one exact run label and short ID. [CITED: .planning/ROADMAP.md] [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

Current local environment is close but not phase-ready: Cargo, Node, Git, Python, and uv are installed, but Ollama is missing and the installed uv version is behind the current PyPI release. No application code or test framework files were found in the repository yet, so Phase 1 planning should include Wave 0 bootstrap tasks. [VERIFIED: environment probe] [VERIFIED: repository scan] [VERIFIED: PyPI registry]

**Primary recommendation:** Build Phase 1 around a single append-only `run + events + raw_items + watchlist_sources` SQLite model, with MicroClaw scheduling/narration on top and a small seed watchlist of verified feeds split by trust tier. [CITED: .planning/research/ARCHITECTURE.md] [CITED: .planning/research/STACK.md]

## Project Constraints (from copilot-instructions.md)

- Work inside a GSD workflow; do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it. [CITED: copilot-instructions.md]
- Treat the project constraints copied from `PROJECT.md` as authoritative: Windows-first, Discord-first, single-user, relevance over volume, visible handoffs in chat, and one end-to-end workflow first. [CITED: copilot-instructions.md] [CITED: .planning/PROJECT.md]
- Use the recommended stack direction already captured in `research/STACK.md`: MicroClaw, Ollama, SQLite/sqlite-vec, Python sidecars, RSS/API-first ingestion, Apify only as fallback, and MicroClaw native Discord by default. [CITED: copilot-instructions.md] [CITED: .planning/research/STACK.md]
- No project skills directories were present in `.github/skills` or `.agents/skills` during this session. [VERIFIED: repository scan]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| MicroClaw | v0.1.50, published 2026-04-11 [VERIFIED: GitHub releases] | Runtime core for Discord delivery, scheduled tasks, persistent runtime state, MCP, and local Web UI. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] | The official README explicitly states Discord support, scheduled tasks, persistent runtime behavior, MCP, and a local web UI, which matches the locked Windows-first Discord-first direction. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| Ollama | v0.20.5, published 2026-04-09 [VERIFIED: GitHub releases] | Local chat/tool/embedding runtime. [CITED: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md] | Official API docs show chat tool support and `POST /api/embed`, which is enough for Phase 1 local model integration and later semantic expansion. [CITED: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md] |
| sqlite-vec | v0.1.9, published 2026-03-31 [VERIFIED: GitHub releases] | Optional semantic retrieval/dedup build path for MicroClaw. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] | MicroClaw documents an optional `--features sqlite-vec` build, so planning should preserve that path even if Phase 1 mostly uses deterministic ingestion and traceability. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| feedparser | 6.0.12, published 2025-09-10 [VERIFIED: PyPI registry] | Default RSS/Atom ingestion parser. [CITED: .planning/research/STACK.md] | Phase 1 is feed-heavy and the project stack already recommends `feedparser` as the default intake layer. [CITED: .planning/research/STACK.md] |
| httpx | 0.28.1, published 2024-12-06 [VERIFIED: PyPI registry] | HTTP client for RSS/API fetches, health checks, and fallback fetch flows. [CITED: .planning/research/STACK.md] | `httpx` is the stack recommendation for source fetches and health probes; Phase 1 needs that more than a heavier framework. [CITED: .planning/research/STACK.md] |
| pydantic | 2.12.5, published 2025-11-26 [VERIFIED: PyPI registry] | Typed schemas for watchlist entries, raw items, runs, and events. [CITED: .planning/research/STACK.md] | Typed boundaries are the simplest way to keep feed/API ingestion, persistence, and status rendering coherent in a greenfield repo. [ASSUMED] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| uv | 0.11.6, published 2026-04-09 [VERIFIED: PyPI registry] | Python package and environment management. [CITED: .planning/research/STACK.md] | Use for Phase 1 bootstrap, but note the local machine currently has uv 0.8.13 installed. [VERIFIED: environment probe] |
| pytest | 9.0.3, published 2026-04-07 [VERIFIED: PyPI registry] | Phase 1 unit/integration validation harness. [CITED: .planning/research/STACK.md] | Use because the repo currently has no test framework files and Phase 1 needs deterministic ingestion/run-state checks. [VERIFIED: repository scan] |
| rapidfuzz | 3.14.5, published 2026-04-07 [VERIFIED: PyPI registry] | Cheap duplicate-title collapse before later canonical-story work. [CITED: .planning/research/STACK.md] | Only use in Phase 1 if identical or near-identical feed items start creating noisy candidate counts. [ASSUMED] |
| @apify/actors-mcp-server | v0.9.17, published 2026-04-08 [VERIFIED: GitHub releases] | Fallback ingestion path for sources without clean feeds/APIs. [CITED: https://raw.githubusercontent.com/apify/actors-mcp-server/master/README.md] | Use only after the Phase 1 allowlist proves a real gap; the hosted server is officially recommended over local stdio for best features. [CITED: https://raw.githubusercontent.com/apify/actors-mcp-server/master/README.md] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MicroClaw scheduler | External schedulers like Airflow/Temporal/Celery | Overkill for one daily workflow and contradicts the locked “one visible workflow first” direction. [CITED: .planning/research/STACK.md] [CITED: .planning/PROJECT.md] |
| RSS/API-first intake | Browser-first scraping | More brittle and directly conflicts with the approved exception-only scraping policy. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| MicroClaw native Discord | Separate Discord bot framework | Splits orchestration from delivery before there is evidence MicroClaw cannot satisfy status-channel needs. [CITED: .planning/research/STACK.md] |

**Installation:** [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] [CITED: .planning/research/STACK.md]
```bash
cargo build --release --features sqlite-vec
microclaw setup
uv pip install feedparser==6.0.12 httpx==0.28.1 pydantic==2.12.5 pytest==9.0.3 rapidfuzz==3.14.5
```

**Version verification:** [VERIFIED: GitHub releases] [VERIFIED: PyPI registry]
- MicroClaw `v0.1.50` — published 2026-04-11. [VERIFIED: GitHub releases]
- Ollama `v0.20.5` — published 2026-04-09. [VERIFIED: GitHub releases]
- sqlite-vec `v0.1.9` — published 2026-03-31. [VERIFIED: GitHub releases]
- feedparser `6.0.12` — published 2025-09-10. [VERIFIED: PyPI registry]
- httpx `0.28.1` — published 2024-12-06. [VERIFIED: PyPI registry]
- pydantic `2.12.5` — published 2025-11-26. [VERIFIED: PyPI registry]
- pytest `9.0.3` — published 2026-04-07. [VERIFIED: PyPI registry]
- rapidfuzz `3.14.5` — published 2026-04-07. [VERIFIED: PyPI registry]

## Architecture Patterns

### Recommended Project Structure
```text
config/
├── watchlist.yaml           # Curated Phase 1 source allowlist [ASSUMED]
src/
├── ingestion/               # RSS/API fetchers, source registry, raw item ingestion [ASSUMED]
├── orchestration/           # run creation, retry logic, manual rerun, status transitions [ASSUMED]
├── visibility/              # Discord narration policy, trace-link rendering, run labels [ASSUMED]
├── persistence/             # SQLite repositories for sources, runs, events, raw_items [ASSUMED]
└── tests/                   # feed fixtures, run-lifecycle tests, Discord renderer tests [ASSUMED]
```

### Pattern 1: One Visible Workflow With Bounded Services
**What:** Use one run coordinator that invokes watchlist load, fetch, persist, narrate, and finalize steps in order. [CITED: .planning/research/ARCHITECTURE.md]  
**When to use:** Entire Phase 1. [CITED: .planning/ROADMAP.md]  
**Why:** The project direction explicitly prefers one visible workflow over a worker mesh, and MicroClaw already provides the runtime loop, scheduling, and chat surfaces. [CITED: .planning/PROJECT.md] [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md]

### Pattern 2: Run-Scoped Event Journal As Source of Truth
**What:** Persist every run milestone to an append-only `run_events` stream, then render both Discord status messages and control-panel traces from that stream. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [CITED: .planning/research/ARCHITECTURE.md]  
**When to use:** Start, ingestion complete, retry scheduled, retry started, final outcome, and operator-triggered reruns. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Why:** This is the cleanest way to satisfy DGST-04 without ad-hoc status strings. [CITED: .planning/REQUIREMENTS.md]

**Recommended Phase 1 run states:** [ASSUMED]
- `created`
- `running`
- `ingestion_complete`
- `retry_pending`
- `completed_with_candidates`
- `completed_no_items`
- `failed`
- `superseded_by_rerun`

**Recommended event types:** [ASSUMED]
- `run.started`
- `source.fetch.started`
- `source.fetch.succeeded`
- `source.fetch.failed`
- `ingestion.completed`
- `retry.scheduled`
- `run.completed`
- `run.no_items`
- `run.failed`
- `run.linked_to_parent`

### Pattern 3: Watchlist Config With Trust Tiers
**What:** Store the starter watchlist in one local config file with explicit `tier`, `kind`, `url`, `topics`, `enabled`, and `poll_minutes` fields. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]  
**When to use:** All source intake in Phase 1. [CITED: .planning/ROADMAP.md]  
**Why:** The user explicitly chose a simple local allowlist and trust-tier model. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

**Recommended starter watchlist:** [VERIFIED: feed URL probe] [ASSUMED]

| Tier | Source | Type | URL | Why start here |
|------|--------|------|-----|----------------|
| official | OpenAI News | RSS | `https://openai.com/news/rss.xml` [VERIFIED: feed URL probe] | Official model/product updates. [ASSUMED] |
| official | Google DeepMind News | RSS | `https://deepmind.google/blog/rss.xml` [VERIFIED: feed URL probe] | Official model/research launches. [ASSUMED] |
| official | Cursor Blog | Atom | `https://cursor.com/atom.xml` [VERIFIED: feed URL probe] | Official AI coding tool updates. [ASSUMED] |
| official | Claude Code releases | GitHub Atom | `https://github.com/anthropics/claude-code/releases.atom` [VERIFIED: feed URL probe] | Satisfies the required GitHub release-feed class for a tracked coding tool. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| official | VS Code Copilot releases | GitHub Atom | `https://github.com/microsoft/vscode-copilot-release/releases.atom` [VERIFIED: feed URL probe] | Official release notes for another high-signal coding tool surface. [ASSUMED] |
| official | Ollama releases | GitHub Atom | `https://github.com/ollama/ollama/releases.atom` [VERIFIED: feed URL probe] | Official local-model/runtime changes. [ASSUMED] |
| curated_tracker | TestingCatalog | RSS | `https://www.testingcatalog.com/rss/` [VERIFIED: feed URL probe] | Good fit for the approved “product tracker” layer. [ASSUMED] |
| trend_watcher | Simon Willison's Weblog | Atom | `https://simonwillison.net/atom/everything/` [VERIFIED: feed URL probe] | Small trend-watcher allowlist candidate. [ASSUMED] |
| trend_watcher | Latent Space | RSS | `https://www.latent.space/feed` [VERIFIED: feed URL probe] | Small trend-watcher allowlist candidate. [ASSUMED] |

**Starter watchlist policy:** [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]
- Start with 8-9 feeds total, not dozens.
- Require `kind in {rss, atom, github_releases}` for Phase 1.
- Reject sources without a clean feed/API.
- Poll official sources every run; do not add near-real-time polling in Phase 1.
- Carry `tier` into later ranking, but in Phase 1 use it mainly for visibility and audit context.

### Pattern 4: Retry and Rerun Lineage, Not Overwrites
**What:** Give retries and manual reruns new `run_id`s and a `parent_run_id` reference. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**When to use:** Automatic retry after scheduled failure and all operator reruns. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Why:** The user explicitly rejected day-level identity overwrite behavior. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

**Recommended identifiers:** [ASSUMED]
- `run_id`: UUID or ULID stored internally.
- `short_run_id`: 4-6 character Crockford Base32 token for human display.
- `run_label`: `YYYY-MM-DD HH:mm local · scheduled|retry|manual · <short_run_id>`.

### Anti-Patterns to Avoid
- **Day-level status overwrite:** Replacing “today’s run” in place destroys traceability for retries and reruns. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **Scraping-first intake:** It violates the locked RSS/API-first direction and adds maintenance before source signal is proven. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- **Chat-only status:** Discord messages without persisted run events create untraceable outcomes. [CITED: .planning/research/ARCHITECTURE.md]
- **Overusing sub-agents in Phase 1:** The architecture note warns that one explicit workflow is the right initial shape. [CITED: .planning/research/ARCHITECTURE.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Daily scheduling | Separate scheduler service or cron mesh | MicroClaw scheduled tasks. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] | The README explicitly documents scheduled tasks and persistence across restarts. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| Discord transport | Standalone Discord bot from scratch | MicroClaw native Discord channel support. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] | Keep orchestration and chat delivery in one runtime until a real gap appears. [CITED: .planning/research/STACK.md] |
| Feed scraping fallback | Custom browser automation first | Feedparser + httpx first; Apify MCP only for exceptions. [CITED: .planning/research/STACK.md] [CITED: https://raw.githubusercontent.com/apify/actors-mcp-server/master/README.md] | Phase 1 scope says scraping is exception-only, and Apify already covers that path if needed. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| Event trace storage | Ad-hoc console logs as truth | Append-only `runs` + `run_events` tables in SQLite. [CITED: .planning/research/ARCHITECTURE.md] | Discord visibility and panel traces should come from the same source of truth. [CITED: .planning/research/ARCHITECTURE.md] |

**Key insight:** Phase 1 should hand-roll only the project-specific policy layer: watchlist config shape, run/event schema, Discord milestone rendering, and trace-link conventions. The runtime, scheduler, channel adapter, and fallback scraping path already have standard answers. [CITED: .planning/notes/visible-routing-architecture.md] [CITED: .planning/research/STACK.md]

## Common Pitfalls

### Pitfall 1: Treating “no qualifying items” as a silent non-event
**What goes wrong:** The user cannot distinguish “workflow failed” from “workflow succeeded but found nothing.” [CITED: .planning/REQUIREMENTS.md]  
**Why it happens:** Teams persist only success/failure and skip a third terminal outcome. [ASSUMED]  
**How to avoid:** Model `completed_no_items` as a first-class final state and emit a dedicated `run.no_items` event plus Discord message. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Warning signs:** A run has raw fetch events but no final outcome event. [ASSUMED]

### Pitfall 2: Logging only final status, not ingestion counts
**What goes wrong:** “Completed” gives no confidence that multi-source intake actually ran. [CITED: .planning/ROADMAP.md]  
**Why it happens:** Status messaging is added after the ingestion pipeline. [ASSUMED]  
**How to avoid:** Persist and display at least source count, source failures, raw items fetched, and candidate items retained. [ASSUMED]  
**Warning signs:** Discord completion messages contain only a generic green check. [ASSUMED]

### Pitfall 3: Letting retry reuse the original run identifier
**What goes wrong:** The visible status cannot tell which attempt produced the final result. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Why it happens:** Retry is implemented as a state mutation instead of a new run. [ASSUMED]  
**How to avoid:** Create a child run for retry and link it back to the failed scheduled run. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Warning signs:** One run record shows both first-failure and later-success timestamps. [ASSUMED]

### Pitfall 4: Planning for a full editable source-management UI
**What goes wrong:** Phase 1 gets delayed by admin UX work unrelated to SRC-01 or DGST-04. [CITED: .planning/REQUIREMENTS.md]  
**Why it happens:** Watchlist management is mistaken for product delivery instead of seed configuration. [ASSUMED]  
**How to avoid:** Ship one repo-local config file first. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
**Warning signs:** Planner tasks mention Discord source-edit commands or control-panel CRUD screens. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]

## Code Examples

Verified patterns from official sources:

### MicroClaw setup and sqlite-vec build
```bash
# Source: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md
cargo build --release --features sqlite-vec
microclaw setup
```

### Ollama embeddings endpoint
```bash
# Source: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md
curl http://localhost:11434/api/embed -d '{
  "model": "all-minilm",
  "input": "Why is the sky blue?"
}'
```

### Recommended watchlist config shape
```yaml
# Source basis: locked local-config + trust-tier decisions in 01-CONTEXT.md
sources:
  - id: openai-news
    tier: official
    kind: rss
    url: https://openai.com/news/rss.xml
    topics: [models, product_updates]
    enabled: true
  - id: claude-code-releases
    tier: official
    kind: github_releases
    url: https://github.com/anthropics/claude-code/releases.atom
    topics: [coding_tools]
    enabled: true
  - id: testingcatalog
    tier: curated_tracker
    kind: rss
    url: https://www.testingcatalog.com/rss/
    topics: [product_updates, trends]
    enabled: true
```
[CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

### Recommended Phase 1 event payload
```json
{
  "run_id": "01JRG3B4K4V1Y2ZQ2R4A5K6M7N",
  "short_run_id": "7K2M",
  "parent_run_id": null,
  "trigger_kind": "scheduled",
  "run_label": "2026-04-11 08:00 local · scheduled · 7K2M",
  "event_type": "ingestion.completed",
  "event_time": "2026-04-11T08:00:41-04:00",
  "source_count": 9,
  "source_successes": 8,
  "source_failures": 1,
  "raw_item_count": 42,
  "candidate_count": 17,
  "trace_url": "http://127.0.0.1:10961/runs/01JRG3B4K4V1Y2ZQ2R4A5K6M7N/events"
}
```
[CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Scraping-first source collection | RSS/API-first intake with scraping only as an exception path. [CITED: .planning/research/STACK.md] | Project direction locked on 2026-04-11. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] | Lower fragility and smaller Phase 1 scope. [ASSUMED] |
| Opaque bot status strings | Run-scoped append-only events rendered into Discord milestone messages and deeper traces. [CITED: .planning/research/ARCHITECTURE.md] | Architecture direction captured 2026-04-11. [CITED: .planning/research/ARCHITECTURE.md] | Satisfies DGST-04 traceability instead of only cosmetic status. [CITED: .planning/REQUIREMENTS.md] |
| Early worker-mesh orchestration | One workflow-oriented local monolith with bounded services. [CITED: .planning/research/ARCHITECTURE.md] | Architecture direction captured 2026-04-11. [CITED: .planning/research/ARCHITECTURE.md] | Easier to debug in a greenfield repo with no implementation yet. [VERIFIED: repository scan] [ASSUMED] |

**Deprecated/outdated:**  
- Broad community/social intake in Phase 1 is out of scope; the approved source model is official plus a small curated industry layer. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]  
- Building a separate control-panel app in v1 is explicitly discouraged by the stack research. [CITED: .planning/research/STACK.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `config/watchlist.yaml` is the right initial file location. | Architecture Patterns | Low; planner can switch the path without affecting phase scope. |
| A2 | A 4-6 character Base32 short run ID is the best human-readable format. | Architecture Patterns | Low; display format can change if collision or UX concerns appear. |
| A3 | Phase 1 should standardize the raw-event trace contract at `/runs/{run_id}/events`, even if a thin adapter is needed. | Code Examples / Open Questions | Medium; if MicroClaw lacks a deep-linkable run view, extra adapter work is needed. |
| A4 | Source-count and candidate-count fields are the minimum useful completion metrics. | Common Pitfalls / Event Model | Low; exact counters can expand. |
| A5 | Rapidfuzz may be worth using in Phase 1 if feed overlap becomes noisy. | Standard Stack | Low; can defer entirely to Phase 2. |

## Open Questions (RESOLVED)

1. **Does MicroClaw already expose a stable deep link to one exact run/event timeline?**
   - Resolution: Standardize Phase 1 on the exact raw-event/log view contract `http://127.0.0.1:10961/runs/<run_id>/events`. Plans 03-04 must verify that MicroClaw already serves this route or provide the thinnest phase-owned adapter that lands there before Discord message text is finalized. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

2. **Can MicroClaw status messages be updated in place, or should Phase 1 plan for separate milestone posts?**
   - Resolution: Phase 1 uses separate milestone posts for `run started`, `ingestion complete`, and `final outcome`; in-place editing is not part of the contract. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

3. **What exact retry delay should the single automatic retry use?**
   - Resolution: Use one automatic retry after exactly 10 minutes. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Cargo | MicroClaw build from source | ✓ [VERIFIED: environment probe] | 1.94.1 [VERIFIED: environment probe] | — |
| Node / npm | Optional Apify MCP fallback tooling | ✓ [VERIFIED: environment probe] | Node 22.18.0 / npm 11.8.0 [VERIFIED: environment probe] | Skip Apify in Phase 1 unless needed. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| Python | Python ingestion sidecar work | ✓ [VERIFIED: environment probe] | 3.13.12 and 3.14.2 executables present [VERIFIED: environment probe] | Install 3.12 with uv only if dependency compatibility requires the project-recommended target version. [CITED: .planning/research/STACK.md] [ASSUMED] |
| uv | Python env/package management | ✓, but older than current release [VERIFIED: environment probe] [VERIFIED: PyPI registry] | local 0.8.13 vs latest 0.11.6 [VERIFIED: environment probe] [VERIFIED: PyPI registry] | Upgrade uv before locking Phase 1 Python tooling. [ASSUMED] |
| Ollama | Local model runtime required by folded setup work | ✗ [VERIFIED: environment probe] | — | No approved fallback; project direction is local-first MicroClaw + Ollama. [CITED: .planning/notes/architecture-repository-mapping.md] [CITED: .planning/research/STACK.md] |
| Discord bot token + allowed channel IDs | Status-channel delivery | Unknown in-session [ASSUMED] | — | Human must provision credentials; MicroClaw documents `discord_bot_token` and channel allowlists. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |

**Missing dependencies with no fallback:**  
- Ollama installation/configuration is blocking for the folded MicroClaw + Ollama prototype objective. [VERIFIED: environment probe] [CITED: .planning/todos/pending/setup-microclaw-ollama-prototype.md]

**Missing dependencies with fallback:**  
- None for the locked Phase 1 scope. [ASSUMED]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Pytest 9.0.3. [VERIFIED: PyPI registry] |
| Config file | none — repo scan found no `pytest.ini`, `pyproject.toml`, or test files yet. [VERIFIED: repository scan] |
| Quick run command | `uv run pytest -q`. [ASSUMED] |
| Full suite command | `uv run pytest -q`. [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SRC-01 | Scheduled/manual run ingests from multiple configured sources and persists source-attributed raw items from more than one watchlist entry. [CITED: .planning/REQUIREMENTS.md] | integration | `uv run pytest tests/test_ingestion_multisource.py -q`. [ASSUMED] | ❌ Wave 0 [VERIFIED: repository scan] |
| DGST-04 | A run records one terminal outcome of `completed_with_candidates`, `completed_no_items`, or `failed`, and the rendered Discord status includes the exact run label/short ID plus trace link. [CITED: .planning/REQUIREMENTS.md] | integration | `uv run pytest tests/test_run_visibility.py -q`. [ASSUMED] | ❌ Wave 0 [VERIFIED: repository scan] |
| DGST-04 | Retry and manual rerun produce distinct run IDs linked to a parent run rather than overwriting status. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] | unit | `uv run pytest tests/test_run_lineage.py -q`. [ASSUMED] | ❌ Wave 0 [VERIFIED: repository scan] |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_run_visibility.py -q` once the test harness exists. [ASSUMED]
- **Per wave merge:** `uv run pytest -q`. [ASSUMED]
- **Phase gate:** Full suite green plus one manual Discord smoke run proving start, ingestion-complete, and final-outcome messages in the status channel. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [ASSUMED]

### Wave 0 Gaps
- [ ] `pyproject.toml` or `pytest.ini` — test config bootstrap. [VERIFIED: repository scan]
- [ ] `tests/test_ingestion_multisource.py` — covers SRC-01. [ASSUMED]
- [ ] `tests/test_run_visibility.py` — covers DGST-04 terminal outcomes and trace link rendering. [ASSUMED]
- [ ] `tests/test_run_lineage.py` — covers retry/rerun traceability. [ASSUMED]
- [ ] Feed fixture directory with recorded RSS/Atom samples from at least three source types. [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no for new phase-owned user auth surfaces. [ASSUMED] | Rely on Discord bot credentials and local operator control rather than inventing app auth in Phase 1. [CITED: .planning/PROJECT.md] |
| V3 Session Management | no for new phase-owned web sessions. [ASSUMED] | Keep the default MicroClaw Web UI local-only at `127.0.0.1:10961`. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| V4 Access Control | yes. [ASSUMED] | Use Discord allowed-channel configuration so status posting is scoped to the intended side channel. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| V5 Input Validation | yes. [ASSUMED] | Validate watchlist entries, feed metadata, and event payloads with Pydantic. [CITED: .planning/research/STACK.md] |
| V6 Cryptography | yes for secret handling, but do not hand-roll crypto. [ASSUMED] | Store Discord/Ollama secrets in environment or local secret config only; rely on platform TLS and runtime libraries. [ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Feed poisoning or malformed XML | Tampering | Parse only allowlisted feeds, validate parsed payloads, and cap content size/timeouts in the fetch layer. [ASSUMED] |
| SSRF via dynamic fallback fetch URLs | Information Disclosure | Never fetch arbitrary user-supplied URLs in Phase 1; only fetch URLs from the curated watchlist. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] |
| Discord bot token leakage | Elevation of Privilege | Keep `discord_bot_token` out of git and configure channel allowlists. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |
| Local control-panel exposure beyond localhost | Information Disclosure | Keep the Web UI on the documented local default binding unless there is an explicit security review. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md` — locked Phase 1 decisions, visibility rules, retry/rerun behavior, and folded todos. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md]
- `.planning/ROADMAP.md` — phase goal, success criteria, and requirement mapping. [CITED: .planning/ROADMAP.md]
- `.planning/REQUIREMENTS.md` — SRC-01 and DGST-04 wording. [CITED: .planning/REQUIREMENTS.md]
- `.planning/research/STACK.md` — approved stack direction for MicroClaw, Ollama, SQLite/sqlite-vec, Python sidecars, and RSS/API-first intake. [CITED: .planning/research/STACK.md]
- `.planning/research/ARCHITECTURE.md` — workflow-oriented local monolith, append-only event trail, and audit-driven visibility model. [CITED: .planning/research/ARCHITECTURE.md]
- `https://raw.githubusercontent.com/microclaw/microclaw/main/README.md` — verified Discord support, scheduled tasks, setup wizard, Web UI default, sqlite-vec build path, MCP transport support, and Discord config keys. [CITED: https://raw.githubusercontent.com/microclaw/microclaw/main/README.md]
- `https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md` — verified tool-capable chat request structure and `POST /api/embed`. [CITED: https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md]
- GitHub release APIs for `microclaw/microclaw`, `ollama/ollama`, `asg017/sqlite-vec`, and `apify/actors-mcp-server`. [VERIFIED: GitHub releases]
- PyPI JSON registry for `feedparser`, `httpx`, `pydantic`, `rapidfuzz`, `pytest`, and `uv`. [VERIFIED: PyPI registry]
- Local environment and repository probes run in this session. [VERIFIED: environment probe] [VERIFIED: repository scan]

### Secondary (MEDIUM confidence)
- `https://raw.githubusercontent.com/apify/actors-mcp-server/master/README.md` — hosted-vs-stdio guidance for the fallback MCP path. [CITED: https://raw.githubusercontent.com/apify/actors-mcp-server/master/README.md]
- Feed URL probes for starter watchlist candidates. [VERIFIED: feed URL probe]

### Tertiary (LOW confidence)
- Exact starter source mix beyond the verified URLs. [ASSUMED]
- Whether MicroClaw serves the resolved `/runs/{run_id}/events` contract natively or via a thin phase-owned adapter. [ASSUMED]
- Exact Discord message-editing capabilities for milestone updates. [ASSUMED]

## Metadata

**Confidence breakdown:**  
- Standard stack: HIGH-MEDIUM — versions and runtime capabilities were verified from official releases/docs, but some phase-specific library choices remain recommendation-level. [VERIFIED: GitHub releases] [VERIFIED: PyPI registry] [ASSUMED]  
- Architecture: HIGH — it is tightly constrained by locked project documents and Phase 1 context. [CITED: .planning/phases/01-ingestion-foundation-run-visibility/01-CONTEXT.md] [CITED: .planning/research/ARCHITECTURE.md]  
- Pitfalls: MEDIUM — grounded in locked requirements and architecture, but some operational failure modes remain experience-based. [CITED: .planning/REQUIREMENTS.md] [ASSUMED]

**Research date:** 2026-04-11. [VERIFIED: session date]  
**Valid until:** 2026-05-11 for project-doc assumptions; re-check official releases before implementation if work starts later. [ASSUMED]
