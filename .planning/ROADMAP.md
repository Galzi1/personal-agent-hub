# Roadmap: Personal Agent Hub

## Overview

This roadmap delivers one explicit daily AI-intelligence workflow from end to end: start with trustworthy multi-source intake and observable run status, turn overlapping coverage into canonical stories, compose a ranked Discord digest with citations and clear relevance cues, then add feedback controls that suppress noise and improve future runs without expanding beyond the core digest loop.

## Phases

**6 phases total (0, 1, 2, 3, 4, 5)**

**Phase Numbering:**
- Integer phases (0, 1, 2, 3, 4, 5): Planned milestone work

- [ ] **Phase 0: Validation Spikes** - De-risk critical assumptions (R1, R3, R4) before committing to implementation. *(Plan 00-01 COMPLETE; Plans 00-02 and 00-03 pending.)*

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
- [ ] 02-01-PLAN.md - format_digest() + post_to_discord() in discord.py, load_discord_config() in config.py, partial status in db.py, all tests green (Wave 1)
- [ ] 02-02-PLAN.md - Wire format_digest + post_to_discord into pipeline.py Step 6, update MicroClaw prompt, add channel_id to config (Wave 2)

### Phase 3: Canonical Story Formation
**Goal**: User gets one trustworthy story per underlying update, with uncertainty visible before stories are selected into the digest.
**Depends on**: Phase 2
**Requirements**: SIG-01, SIG-04
**Success Criteria** (what must be TRUE):
  1. User receives one story candidate per underlying update even when many sources cover the same event.
  2. User does not see the same underlying update repeated as separate stories after duplicate coverage is collapsed.
  3. User can distinguish confirmed updates from uncertain or disputed items.
**Architecture notes**:
  - Introduce a `memory` table placeholder in SQLite alongside canonical stories - dedup/clustering benefits from remembering past story patterns, and Phase 5 memory promotion will extend this schema rather than retrofitting it.
  - Research `topoteretes/cognee` (knowledge graphs) and `vectorize-io/hindsight` (learning memory) during Phase 3 planning to inform the memory schema shape.
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md - Define memory/story tables and deduplication pipeline
- [ ] 03-02-PLAN.md - Integrate Cognee Knowledge Engine and Story Recall API

### Phase 4: Ranked Discord Digest
**Goal**: User receives a short, relevant, topic-aware daily digest in Discord that explains why each selected story matters.
**Depends on**: Phase 3
**Requirements**: SRC-02, SIG-02, SIG-03, DGST-01, DGST-02, DGST-03
**Success Criteria** (what must be TRUE):
  1. User receives the daily digest in Discord.
  2. User can scan separate digest sections for model releases, AI coding tools, new AI tools, and hot trends.
  3. User receives a ranked shortlist of the most relevant daily stories instead of a raw chronological feed.
  4. Each digest item includes supporting source citations and a short "why it matters" explanation.
  5. User can define tracked topics that influence what appears in the digest.
**Architecture notes**:
  - Formalize observability metrics during this phase: ingestion latency, source success rate, dedup compression ratio, ranking confidence distribution. These feed the Control Panel's Activity view from the architecture diagram.
  - Keep agent system prompts minimal - use examples and memory for calibration, not instruction bloat (lesson from Squid Club multi-agent article).
**Plans**: 2 plans

Plans:
- [ ] 04-01-PLAN.md - Design ranking rubrics and section templates
- [ ] 04-02-PLAN.md - Implement topic-aware ranking and sectioning

### Phase 5: Feedback & Suppression
**Goal**: User can calibrate future digests directly by suppressing noise and marking which items were useful.
**Depends on**: Phase 4
**Requirements**: FDBK-01, FDBK-02, FDBK-03
**Success Criteria** (what must be TRUE):
  1. User can mute a source so it no longer appears in future digests.
  2. User can mute a topic so it no longer appears in future digests.
  3. User can mark a digest item as more useful or less useful with simple feedback controls.
  4. User can observe later digests reflecting those mute and usefulness signals.
**Architecture notes**:
  - Save positive feedback alongside corrections - agents that only learn from mistakes become overly cautious (lesson from Squid Club multi-agent article).
  - Extend the Phase 3 memory schema placeholder with promotion rules: logs → durable memory requires explicit validation, not automatic promotion.
  - Research `topoteretes/cognee` and `vectorize-io/hindsight` for memory engine options beyond raw SQLite.
**Plans**: 2 plans

Plans:
- [ ] 05-01-PLAN.md - Define feedback schema and mute logic
- [ ] 05-02-PLAN.md - Implement interactive feedback loops

## Progress

**Execution Order:**
Phases execute in numeric order: 0 → 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Validation Spikes | 3/3 | Complete | 2026-04-24 |
| 1. Ingestion Foundation & Run Visibility | 4/4 | Complete | 2026-04-26 |
| 2. Thin Digest | 0/2 | Planned | - |
| 3. Canonical Story Formation | 0/2 | Not started | - |
| 4. Ranked Discord Digest | 0/2 | Not started | - |
| 5. Feedback & Suppression | 0/2 | Not started | - |

## Risk Register

See `.planning/RISK-REVIEW.md` for the full risk register (R1-R10), assumption analysis, and recommended actions.

**Top risks informing roadmap structure:**
- ~~**R1 (Critical):** MicroClaw proves insufficient~~ - **CLOSED 2026-04-23** via Plan 00-01 GO
- **R2 (High):** Long time to first useful digest - mitigated by Phase 2 thin digest milestone
- **R3 (High):** OpenRouter-hosted model quality unverified - mitigated by Phase 0 Plan 00-02 evaluation (per-task starters from D-18)
