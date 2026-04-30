# Milestones: Personal Agent Hub

## v1.0 MicroClaw AI Digest MVP

**Status:** In Progress  
**Started:** 2026-04-23  
**Goal:** Deliver a fully functional, scheduled, self-healing AI digest pipeline on MicroClaw.

**Phases:** 0–6

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 0 | Validation Spikes | Complete | 2026-04-24 |
| 1 | Ingestion Foundation & Run Visibility | Complete | 2026-04-26 |
| 2 | Thin Digest | Complete | 2026-04-27 |
| 3 | Source Coverage Fix | Planned | - |
| 4 | Daily Scheduling | Planned | - |
| 5 | Self-Healing Missed Digests | Planned | - |
| 6 | URL Deduplication | Planned | - |

**Requirements delivered:**
- SRC-01: Multi-source watchlist ingestion (Phase 1)
- DGST-04: Run visibility in Discord (Phase 1)
- DGST-01: Daily digest posted to Discord (Phase 2)

**Requirements remaining:**
- SRC-02: Topic tracking (Phase 3)
- SIG-01: URL deduplication (Phase 6)

**Key decisions:**
- MicroClaw validated as platform foundation (Plan 00-01 GO, 2026-04-23)
- OpenRouter model quality validated (Plan 00-02 GO, 2026-04-24)
- Thin digest milestone added to mitigate R2 (long time to first value)

---

## v2.0 NanoClaw Migration

**Status:** Planned  
**Depends on:** v1.0 complete (Phase 6 done)  
**Goal:** Validate Nanoclaw as viable migration target, then migrate the pipeline from MicroClaw to Nanoclaw.

**Phases:** 7–8

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 7 | Nanoclaw Capability Spike | Planned | - |
| 8 | Nanoclaw Migration | Planned | - |

**Requirements delivered:** None (platform migration - no user-facing requirements)

**Gate:** Phase 8 blocked unless Phase 7 records a GO verdict.

**Key decisions:**
- Nanoclaw chosen as migration target (lighter-weight successor to MicroClaw, 27k★ vs 643★)
- Spike-before-commit pattern (Phase 7) mirrors Phase 0 approach for MicroClaw

---

## v3.0 Reliability Enhancements

**Status:** Planned  
**Depends on:** Phase 2 complete (can begin after thin digest; runs parallel to M1/M2 remaining phases)  
**Goal:** Make the pipeline debuggable and the digest output high-signal via persistent logs and relevance ranking.

**Phases:** 9–10

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 9 | Persistent Searchable Logs | Planned | - |
| 10 | Ranked Digest | Planned | - |

**Requirements delivered:**
- SIG-02: Ranked shortlist of most relevant daily stories (Phase 10)
- SIG-03: "Why it matters" explanation per item (Phase 10)
- DGST-02: Citations to supporting source links (Phase 10)
- DGST-03: Digest sections by category (Phase 10)

**Key decisions:**
- OpenSearch vs Elasticsearch: evaluate for Windows-friendly local dev setup (Phase 9)
- Structured JSON log events (not free-text) to enable field-level queries (Phase 9)
- Digest capped at top 10 items (Phase 10)

---
*Last updated: 2026-04-27*
