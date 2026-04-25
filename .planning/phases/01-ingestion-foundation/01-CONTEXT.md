# Phase 1: Ingestion Foundation & Run Visibility - Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Bootstrap the pipeline that gathers AI news items from validated RSS feeds and makes each daily run outcome visible in Discord. No ranking, deduplication, or digest formatting yet - just ingest + relevance pre-filter + run status.

**Requirements in scope:** SRC-01, DGST-04

**Success criteria:**
1. User receives candidate updates gathered from curated multi-source watchlist (7 verified feeds from Phase 0 spike)
2. User can see whether each daily run completed, failed, or produced no qualifying items (Discord status message)
3. User can identify which daily run produced the visible outcome (run ID in every message)

</domain>

<decisions>
## Implementation Decisions

### Source Configuration
- **D-01:** Feed URLs live in `config/sources.yaml` alongside `models.yaml`. Consistent with D-19 (all YAML in one `config/` folder). Phase 4 mute-a-source writes to this same file.
- **D-02:** Schema: each entry has `name`, `url`, `enabled` (bool), and optional `note` (human-readable metadata). Phase 1 does not act on `note` - it is stored for future phases and human readers.
- **D-03:** Starting with the 7 verified feeds from spike 00-03. Notes pre-populated for noisy sources: OpenAI Blog (mixes academy/tutorial content), Simon Willison (high volume minor links), Ollama Releases (frequent RC/patch noise).
- **D-04:** Cursor Changelog and Anthropic Blog are documented as UNAVAILABLE (no RSS endpoint) in sources.yaml. Not active sources in Phase 1.

### Relevance Pre-Filter (OpenRouter in hot path)
- **D-05:** Phase 1 includes a light AI-relevance pre-filter via OpenRouter on every daily run. Items pass if they are about: new model releases, AI coding tools, new AI tools, notable AI product updates, or hot AI trends. Items discarded: tutorials/academy content, non-AI software releases, minor link posts unrelated to AI.
- **D-06:** New task type `relevance` added to `config/models.yaml`. Starter model: same as `ranking` (Gemini Flash Preview or equivalent per D-18 fallback chain). Per D-15/D-17: config-driven, no hardcoded model IDs.
- **D-07:** Relevance check uses title + summary fields only (no extra HTTP fetch). Fast, low-cost per item.

### Run Status Discord UX
- **D-08:** Three distinct Discord message formats, one per run outcome:
  - **Success:** `✅ Run #N - YYYY-MM-DD HH:MM\n{raw} fetched → {relevant} relevant items from {n} sources`
  - **Failure:** `❌ Run #N failed - YYYY-MM-DD HH:MM\n{error reason}\nRun ID: run-N-YYYY-MM-DD`
  - **No items:** `⚠️ Run #N - YYYY-MM-DD HH:MM\n0 relevant items (all sources returned no new AI content)`
- **D-09:** Run ID included in every message for traceability. Format: `run-{N}-{YYYY-MM-DD}`.
- **D-10:** Success message shows both raw fetch count and post-filter relevant count so over-aggressive filtering is visible.
- **D-11:** Plan 01-04's "3 separate Discord milestone posts" are dev-time run markers (bootstrap, ingestion, schedule registration) - not the same as the daily run-status UX defined in D-08/D-10.

### Raw Item SQLite Schema
- **D-12:** `raw_items` table stores 8 fields per item:
  ```
  id            TEXT  -- uuid
  run_id        TEXT  -- FK to runs table
  source_name   TEXT  -- e.g., "OpenAI Blog"
  title         TEXT
  link          TEXT
  published_at  TEXT  -- ISO datetime (feedparser date precedence: published_parsed → updated_parsed → created_parsed)
  summary       TEXT  -- RSS description/summary field
  ingested_at   TEXT  -- when stored
  ```
- **D-13:** Phase 1 stores items that PASS the relevance filter. Discarded items are not stored (no "rejected" table in Phase 1).
- **D-14:** `runs` table tracks each execution: `run_id`, `run_number`, `started_at`, `completed_at`, `status` (success/failure/no_items), `raw_count`, `relevant_count`, `error_message`.

### Schedule & Runtime
- **D-15:** Daily run scheduled at 08:00 local Windows time via MicroClaw scheduler (per Plan 01-04).
- **D-16:** Phase 1 is outbound-only (D-24 from Phase 0). No inbound user flows in this phase.

### Claude's Discretion
- SQLite schema migrations approach (direct CREATE TABLE or lightweight migration)
- Retry/timeout defaults for the httpx feed fetch calls
- Relevance filter prompt design (few-shot examples vs zero-shot)
- Batch vs per-item OpenRouter calls for the relevance filter (cost/latency tradeoff)
- Test fixture strategy for Phase 1 test harness

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 0 Spike Results
- `.planning/phases/00-validation-spikes/00-CONTEXT.md` - All Phase 0 locked decisions (D-01 through D-24). Critical: D-13/D-14 (OpenRouter sole provider), D-15 (per-task model selection), D-17 (no hardcoded model IDs), D-19/D-20/D-21 (config layout), D-23/D-24 (outbound-only, @-mention contract).
- `.planning/phases/00-validation-spikes/00-03-SPIKE-RESULTS.md` - 7 verified feed URLs for direct reuse. Feedparser+httpx pattern. Notes on noisy sources.
- `.planning/phases/00-validation-spikes/00-03-SUMMARY.md` - Date field fallback chain pattern, per-source volume observations.
- `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md` - MicroClaw contracts (F1: @-mention required for inbound; F2-F4: other findings).

### Project Requirements
- `.planning/REQUIREMENTS.md` - SRC-01 and DGST-04 are the Phase 1 requirements.
- `.planning/PROJECT.md` - Core constraints: Windows-first, Discord delivery, planning guard (no new artifacts until current plan passing tests).

### Risk Register
- `.planning/RISK-REVIEW.md` - R2 (time to first useful digest → mitigated by Phase 1.5), R6 (over-planning guard).

### Existing Config
- `config/models.yaml` - Phase 1 adds `relevance` task type to this file. Must not break existing task keys.
- `config/microclaw.config.yaml` - OpenRouter API key lives here (D-20). Phase 1 code reads from this path.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `spikes/spike_watchlist.py` - Reference implementation for `httpx.get() → feedparser.parse(response.text)` pattern with date fallback chain. Copy/adapt ingestion logic from here - do not call feedparser with URLs directly.
- `spikes/spike_openrouter.py` - Reference OpenRouter client pattern (httpx-based). Adapt for relevance filter calls.
- `config/models.yaml` - Already exists with D-18 task assignments. Phase 1 adds `relevance` key.
- `config/microclaw.config.yaml` - Already exists and gitignored. OpenRouter key stored here.

### Established Patterns
- **Feed fetch pattern:** `httpx.get(url, headers={"User-Agent": "..."}) → feedparser.parse(response.text)` (no rate limiting observed in spike)
- **Date precedence chain:** `published_parsed → updated_parsed → created_parsed` (from 00-03-SUMMARY.md)
- **Config in `config/` folder** (D-19): all YAML config files live there
- **No hardcoded model IDs** (D-17): all model references via `config/models.yaml`
- **Secrets gitignored** (D-20): `config/microclaw.config.yaml` holds tokens, not tracked

### Integration Points
- MicroClaw runtime: scheduler triggers the daily run at 08:00; Discord adapter posts the status message
- OpenRouter: relevance pre-filter calls go through existing OpenRouter HTTP client pattern from spike
- SQLite: `C:\Users\galzi\.microclaw\microclaw.db` - shared runtime DB (Phase 1 adds `raw_items` and `runs` tables)

</code_context>

<specifics>
## Specific Ideas

- Run status success format (user confirmed): `✅ Run #42 - 2026-04-25 08:01\n18 fetched → 12 relevant items from 7 sources`
- Run status failure format (user confirmed): `❌ Run #43 failed - 2026-04-25 08:01\nOpenRouter unreachable after 3 retries\nRun ID: run-43-2026-04-25`
- Run status no-items format (user confirmed): `⚠️ Run #44 - 2026-04-26 08:01\n0 items ingested (all sources returned no new items)`
- sources.yaml note for Ollama: "High RC/patch noise - consider grouping in digest"
- sources.yaml note for OpenAI Blog: mixes academy/tutorial content with news
- sources.yaml note for Simon Willison: high volume, includes minor links alongside real news

</specifics>

<deferred>
## Deferred Ideas

- **Per-source filtering rules** (beyond human-readable `note`): machine-actionable filter hints per source deferred to Phase 2 ranking/dedup. Phase 1 only stores the notes.
- **Control panel model-selection UI**: tracked from Phase 0 deferred. Config file edit is sufficient for Phase 1.
- **DM-based bot-receiver flow**: deferred from Phase 0 (D-23/D-24). No inbound flows until Phase 2+.
- **`rejected_items` table**: discarded items not stored in Phase 1. May be wanted in Phase 2 for debugging filter quality.

</deferred>

---

*Phase: 01-ingestion-foundation*
*Context gathered: 2026-04-25*
