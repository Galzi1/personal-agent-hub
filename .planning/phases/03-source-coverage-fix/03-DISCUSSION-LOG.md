# Phase 3: Source Coverage Fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 3-source-coverage-fix
**Areas discussed:** Item selection before filter, Per-source count visibility, Coverage enforcement policy

---

## Item Selection Before Filter

| Option | Description | Selected |
|--------|-------------|----------|
| Per-source cap | Take first N items per source before pooling. Prevents any source from taking >N slots. | |
| Recency window first | Drop items older than 48h before LLM filter. Semantically correct - old items shouldn't be in today's digest. | ✓ |
| Raise global cap only | Bump 50 → 150+. Simpler but doesn't prevent source starvation if one source returns 100 items. | |

**User's choice:** Recency window first

**Follow-up - window size:**

| Option | Description | Selected |
|--------|-------------|----------|
| 48 hours | Covers weekend gaps and slow sources (DeepMind ~2/week). | ✓ |
| 24 hours | Matches digest cadence exactly but may exclude slow sources on quiet days. | |
| 72 hours | More buffer but 3-day-old items feel stale. | |

**Follow-up - empty sources:**

| Option | Description | Selected |
|--------|-------------|----------|
| Skip silently | logger.warning per source with 0 items in window. No forced inclusions. | ✓ |
| Fallback: include newest item anyway | Force-include most recent item regardless of age. Guarantees participation but may post week-old news. | |

**Follow-up - safety cap:**

| Option | Description | Selected |
|--------|-------------|----------|
| Keep cap, raise to 150 | Safety backstop for burst days after recency window. | ✓ |
| No cap - send all 48h items | Cleaner logic but a major launch day could send 200+ items to OpenRouter. | |
| Keep 50 (apply after window) | 50 is too tight - same starvation problem. | |

**Notes:** Root cause confirmed via code reading - `filter.py:44` uses `items[:50]` globally. OpenAI Blog is first in `sources.yaml` and likely returns 30+ items, consuming most slots. Recency window is semantically cleaner than a per-source cap because it also removes stale content independent of the coverage fix.

---

## Per-Source Count Visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Logger + Discord status | Per-source counts in logger AND Discord success message breakdown line. | ✓ |
| Logger only | Console log only - cleaner Discord but regressions require log inspection. | |
| Logger + SQLite table | Queryable history but requires schema addition. Discord unchanged. | |

**User's choice:** Logger + Discord status

**Follow-up - when to show breakdown:**

| Option | Description | Selected |
|--------|-------------|----------|
| Success only | Breakdown only when items exist. No-items/failure messages unchanged per Phase 1 D-08. | ✓ |
| All outcomes including no_items | Useful to confirm what each source returned (all zeros). | |

**Notes:** User confirmed the Discord format preview:
```
✅ Run #5 - 2026-04-28 09:00
18 fetched → 9 relevant from 4 sources
(OpenAI Blog: 3, TestingCatalog: 3, Simon Willison: 2, Latent Space: 1)
Run ID: run-5-2026-04-28
```
`source_count` in the status line now means contributing sources, not configured/enabled sources.

---

## Coverage Enforcement Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Discord warning | ⚠️ inline on source count + separate warning line when <3 sources. | ✓ |
| Log only (passive) | logger.warning only. No Discord alert. | |
| Force-include top item per source | Override filter to guarantee source diversity. May include low-quality items. | |

**User's choice:** Discord warning

**Notes:** User confirmed the warning format preview:
```
✅ Run #5 - 2026-04-28 09:00
11 fetched → 4 relevant from 2 sources ⚠️
(OpenAI Blog: 3, Latent Space: 1)
⚠️ Only 2 sources represented - check filters
Run ID: run-5-2026-04-28
```
Threshold is 3 (per ROADMAP SC2). No forced inclusions - fixing coverage requires config or filter change, not automatic override.

---

## Claude's Discretion

- Where recency window logic lives (inline in pipeline vs. helper function)
- Exact datetime comparison approach (UTC-aware timedelta)
- Whether `format_digest()` receives `source_breakdown: dict[str, int]` param or derives it from items
- How the breakdown line handles very long source names (truncation)
- The 48h window and 150-item cap as named constants vs. configurable values

## Deferred Ideas

- Per-source configurable recency window (e.g., 72h for DeepMind) - global 48h sufficient for Phase 3
- SQLite `source_stats` table for queryable history - Discord breakdown covers Phase 3 goal
- Machine-actionable per-source filter rules (beyond human notes in sources.yaml)
