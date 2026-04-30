# Roadmap: Personal Agent Hub

## Overview

This roadmap delivers one explicit daily AI-intelligence workflow from end to end: start with trustworthy multi-source intake and observable run status, turn overlapping coverage into a ranked Discord digest with clear relevance cues, then harden the pipeline with deduplication, scheduling, self-healing, observability, and a clean platform migration.

## Phases

**11 phases total (0–10)**

**Phase Numbering:**
- Integer phases (0–10): Planned milestone work

---

## Milestone 1: MicroClaw AI Digest MVP

Phases 0–6. Delivers a fully functional, scheduled, self-healing digest pipeline on MicroClaw.

- [x] **Phase 0: Validation Spikes** - COMPLETE 2026-04-24
- [x] **Phase 1: Ingestion Foundation & Run Visibility** - COMPLETE 2026-04-26
- [x] **Phase 2: Thin Digest** - COMPLETE 2026-04-27
- [ ] **Phase 3: Source Coverage Fix** - Ensure all sources are represented in digests
- [ ] **Phase 4: Daily Scheduling** - 9:00 AM Israel time cron
- [ ] **Phase 5: Self-Healing Missed Digests** - Send digest on startup if scheduled run was missed
- [ ] **Phase 6: URL Deduplication** - Persistent seen-URLs DB, no item repeats across digests

---

## Milestone 2: NanoClaw Migration

Phases 7–8. Validates and executes migration from MicroClaw to Nanoclaw.

- [ ] **Phase 7: Nanoclaw Capability Spike** - Validate Nanoclaw as viable migration target before committing to it
- [ ] **Phase 8: Nanoclaw Migration** - Migrate from MicroClaw to Nanoclaw

---

## Milestone 3: Reliability Enhancements

Phases 9–10. Adds observability and a ranked, annotated digest format.

- [ ] **Phase 9: Persistent Searchable Logs** - Pipeline and agent logs to OpenSearch/Elasticsearch
- [ ] **Phase 10: Ranked Digest** - Minimal ranking pass on ingested items

---

### Phase 0: Validation Spikes
**Goal**: Validate that MicroClaw, OpenRouter, and the starter watchlist are sufficient for v1 before writing application code.
**Depends on**: Nothing
**Requirements**: R1, R3, R4 (risk mitigation)
**Success Criteria** (what must be TRUE):
  1. MicroClaw spike confirms scheduler, Discord posting, and SQLite persistence work on Windows (R1).
  2. OpenRouter API evaluation on 10-20 representative ranking/summarization tasks meets minimum quality bar (R3).
  3. Watchlist backtest against one real week of AI news shows acceptable coverage (R4).
**Plans**: 3 plans

Plans:
- [x] 00-01-PLAN.md - Install MicroClaw, smoke-test 4 critical capabilities (scheduler, Discord, SQLite, control panel), record go/no-go. **COMPLETE 2026-04-23 - GO.**
- [x] 00-02-PLAN.md - Evaluate OpenRouter per-task starter model assignments (D-18) on 10-15 tasks; verify availability/quality; record R3 go/no-go. **COMPLETE 2026-04-24 - GO.**
- [x] 00-03-PLAN.md - Fetch 9 starter RSS feeds, collect recent items, user reviews coverage against real AI news week; record R4 go/no-go. **COMPLETE 2026-04-24 - GO.**


### Phase 1: Ingestion Foundation & Run Visibility
**Goal**: User can rely on a local-first daily digest workflow that gathers candidate updates from a curated watchlist and makes each run outcome visible.
**Depends on**: Nothing (first phase)
**Requirements**: SRC-01, DGST-04
**Success Criteria** (what must be TRUE):
  1. User receives candidate updates gathered from a curated multi-source watchlist rather than a single feed.
  2. User can see whether the daily digest run completed, failed, or produced no qualifying items.
  3. User can tell which daily run produced the visible outcome instead of seeing an untraceable status message.
**Plans**: 4 plans

Plans:
- [x] 01-01-PLAN.md - Bootstrap uv/pytest project, relocate microclaw config, sources.yaml with 7 verified feeds, Wave 0 test stubs (15 tests passing) **COMPLETE 2026-04-26.**
- [x] 01-02-PLAN.md - config.py + ingester.py (RawItem, fetch_feed) + filter.py (relevance_filter); SRC-01 tests green **COMPLETE 2026-04-26.**
- [x] 01-03-PLAN.md - db.py (runs + raw_items schema, CRUD) + discord.py (D-08 format helpers) + pipeline.py (run_digest orchestrator); DGST-04 tests green **COMPLETE 2026-04-26.**
- [x] 01-04-PLAN.md - Live wiring: real OpenRouter key, live pipeline run, 3 milestone Discord posts, 08:00 recurring schedule registration **COMPLETE 2026-04-26.**

### Phase 2: Thin Digest
**Goal**: Post a simple formatted list of ingested items to Discord daily, giving the user a tangible artifact before dedup and ranking exist.
**Depends on**: Phase 1
**Requirements**: None (risk mitigation for R2 - early value delivery)
**Success Criteria** (what must be TRUE):
  1. User receives a daily Discord message listing ingested items with source and title.
  2. End-to-end pipeline (schedule, ingest, format, deliver) is validated.
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md - format_digest() + post_to_discord() in discord.py, load_discord_config() in config.py, partial status in db.py, all tests green (Wave 1) **COMPLETE 2026-04-27.**
- [x] 02-02-PLAN.md - Wire format_digest + post_to_discord into pipeline.py Step 6, update MicroClaw prompt, add channel_id to config (Wave 2) **COMPLETE 2026-04-27.**

### Phase 3: Source Coverage Fix
**Goal**: Ensure the digest consistently draws items from multiple sources, not a single dominant feed.
**Depends on**: Phase 2
**Context**: First live run produced items exclusively from OpenAI Blog; other configured sources were ignored or filtered out.
**Success Criteria** (what must be TRUE):
  1. Diagnose why only one source contributed items in the first live run.
  2. Items from at least 3 distinct sources appear in each digest (when available).
  3. Per-source item counts are logged so regressions are visible.
**Plans**: 1 plan

Plans:
- [ ] 03-01-PLAN.md - Add recency window (48h), raise filter cap 50→150, per-source breakdown in Discord, coverage warning

### Phase 4: Daily Scheduling
**Goal**: Digest runs automatically at 9:00 AM Israel time (Asia/Jerusalem) every day without manual invocation.
**Depends on**: Phase 2
**Success Criteria** (what must be TRUE):
  1. MicroClaw (or system scheduler) fires `run_digest` at 09:00 Asia/Jerusalem daily.
  2. Timezone is explicit in config, not hardcoded.
  3. Schedule survives a machine reboot.
**Plans**: 1 plan

Plans:
- [ ] 04-01-PLAN.md - Configure 09:00 Asia/Jerusalem recurring schedule, verify post-reboot persistence

### Phase 5: Self-Healing Missed Digests
**Goal**: If the machine was off at the scheduled time, the digest runs automatically once the process starts - catching up rather than silently skipping.
**Depends on**: Phase 4
**Context**: MicroClaw scheduler may not support missed-run detection natively; may need a startup hook or last-run timestamp check.
**Success Criteria** (what must be TRUE):
  1. On startup, pipeline checks the last successful run timestamp.
  2. If no digest was posted today (local date), a catch-up run fires automatically.
  3. Catch-up runs are logged distinctly from scheduled runs.
**Architecture notes**:
  - The `runs` table already tracks `run_number`, `status`, and timestamp - last-run check should query this table.
  - Investigate whether MicroClaw's scheduler supports a "missed window" option before building a custom startup hook.
**Plans**: 1 plan

Plans:
- [ ] 05-01-PLAN.md - Implement startup catch-up logic using runs table, log catch-up runs, tests

### Phase 6: URL Deduplication
**Goal**: No digest item URL ever appears in more than one daily digest.
**Depends on**: Phase 2
**Success Criteria** (what must be TRUE):
  1. A persistent `seen_urls` table in SQLite stores every URL that has appeared in a posted digest.
  2. Pipeline filters out any item whose URL is already in `seen_urls` before formatting.
  3. After posting, all new item URLs are inserted into `seen_urls`.
**Plans**: 1 plan

Plans:
- [ ] 06-01-PLAN.md - Add seen_urls table, insert-on-post logic, filter-before-format logic, tests

### Phase 7: Nanoclaw Capability Spike
**Goal**: Validate that Nanoclaw is a viable migration target before phases 8–10 deepen MicroClaw entanglement.
**Depends on**: Phase 6
**Context**: Nanoclaw (https://github.com/qwibitai/nanoclaw) is the planned Phase 8 migration target. Gaps discovered late (after phases 5–6) are expensive; discovering them now is cheap. Analogous to Phase 0 Plan 00-01 for MicroClaw.
**Success Criteria** (what must be TRUE):
  1. Nanoclaw supports scheduler, Discord posting, and SQLite persistence on Windows - or gaps are documented.
  2. Startup hook capability (needed by Phase 5 self-healing) is confirmed present or absent.
  3. Go/no-go recorded: GO means Phase 8 proceeds as planned; NO-GO means Phase 8 is dropped and MicroClaw is retained.
**Plans**: 1 plan

Plans:
- [ ] 07-01-PLAN.md - Install Nanoclaw, smoke-test scheduler/Discord/SQLite/startup-hook on Windows, document gaps vs MicroClaw, record go/no-go

### Phase 8: Nanoclaw Migration
**Goal**: Migrate the pipeline from MicroClaw to Nanoclaw as the hosting platform.
**Depends on**: All prior phases stable; Phase 7 go/no-go must be GO
**Context**: Nanoclaw (https://github.com/qwibitai/nanoclaw) is a lighter-weight successor; migration should preserve all existing scheduling, Discord posting, and scheduling behaviors.
**Success Criteria** (what must be TRUE):
  1. Pipeline runs identically under Nanoclaw as it did under MicroClaw.
  2. Scheduling, Discord posting, and startup catch-up all work post-migration.
  3. MicroClaw config artifacts are retired or converted.
**Plans**: 2 plans

Plans:
- [ ] 08-01-PLAN.md - Execute migration, retire MicroClaw config, validate full pipeline
- [ ] 08-02-PLAN.md - Validate scheduling, Discord posting, and startup catch-up under Nanoclaw

### Phase 9: Persistent Searchable Logs
**Goal**: All pipeline and agent logs are written to a persistent, searchable store (OpenSearch or Elasticsearch) so debugging and monitoring don't rely on ephemeral console output.
**Depends on**: Phase 2
**Success Criteria** (what must be TRUE):
  1. Every pipeline run emits structured log events to the log store.
  2. Logs are queryable by run ID, timestamp, and log level.
  3. Local SQLite run status is complemented (not replaced) by the log store.
**Architecture notes**:
  - Evaluate OpenSearch vs Elasticsearch for Windows-friendly local dev setup.
  - Use structured JSON log events (not free-text strings) to enable field-level queries.
**Plans**: 2 plans

Plans:
- [ ] 09-01-PLAN.md - Stand up local OpenSearch/Elasticsearch, define log schema, wire pipeline logging
- [ ] 09-02-PLAN.md - Add agent-level log emission, verify queryability, document retention policy

### Phase 10: Ranked Digest
**Goal**: User receives a short ranked list of the most relevant daily items in Discord, each with a brief "why it matters" note.
**Depends on**: Phase 3
**Requirements**: DGST-01, DGST-02, DGST-03
**Success Criteria** (what must be TRUE):
  1. Ingested items are scored and sorted by relevance before posting.
  2. Each digest item includes a one-line "why it matters" explanation.
  3. Digest is capped at a sensible max item count (e.g. top 10).
**Plans**: 2 plans

Plans:
- [ ] 10-01-PLAN.md - Implement relevance scoring (LLM-based or heuristic) and sort pipeline output
- [ ] 10-02-PLAN.md - Add "why it matters" generation per item and cap digest length

---

## Progress

**Execution Order:**
Within each milestone, phases execute in numeric order. Milestone 2 begins after Milestone 1 is complete. Milestone 3 phases (9–10) can begin after Phase 2.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| **Milestone 1: MicroClaw AI Digest MVP** | | | |
| 0. Validation Spikes | 3/3 | Complete | 2026-04-24 |
| 1. Ingestion Foundation & Run Visibility | 4/4 | Complete | 2026-04-26 |
| 2. Thin Digest | 2/2 | Complete | 2026-04-27 |
| 3. Source Coverage Fix | 0/1 | Planned | - |
| 4. Daily Scheduling | 0/1 | Planned | - |
| 5. Self-Healing Missed Digests | 0/1 | Planned | - |
| 6. URL Deduplication | 0/1 | Planned | - |
| **Milestone 2: NanoClaw Migration** | | | |
| 7. Nanoclaw Capability Spike | 0/1 | Planned | - |
| 8. Nanoclaw Migration | 0/2 | Planned | - |
| **Milestone 3: Reliability Enhancements** | | | |
| 9. Persistent Searchable Logs | 0/2 | Planned | - |
| 10. Ranked Digest | 0/2 | Planned | - |

## Risk Register

See `.planning/RISK-REVIEW.md` for the full risk register (R1-R10), assumption analysis, and recommended actions.

**Top risks informing roadmap structure:**
- ~~**R1 (Critical):** MicroClaw proves insufficient~~ - **CLOSED 2026-04-23** via Plan 00-01 GO
- **R2 (High):** Long time to first useful digest - mitigated by Phase 2 thin digest milestone *(delivered 2026-04-27)*
- **R3 (High):** OpenRouter-hosted model quality unverified - mitigated by Phase 0 Plan 00-02 evaluation (per-task starters from D-18)
