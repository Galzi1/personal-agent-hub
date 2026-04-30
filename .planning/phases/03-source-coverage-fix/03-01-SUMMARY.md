---
phase: 03-source-coverage-fix
plan: 01
subsystem: pipeline
tags: [filter, discord, recency-window, source-coverage, logging]

requires:
  - phase: 02-thin-digest
    provides: filter.py with relevance_filter, discord.py with format_digest/format_success

provides:
  - apply_recency_window() in filter.py with RECENCY_HOURS=48 and FILTER_CAP=150
  - source_breakdown dict derivation in pipeline.py
  - Per-source counts in Discord success message with coverage warning when <3 sources

affects: [pipeline, discord, filter, future phases that call format_digest or format_success]

tech-stack:
  added: []
  patterns: [recency-window before LLM filter, source-breakdown dict over scalar count]

key-files:
  created: []
  modified:
    - src/agent_hub/filter.py
    - src/agent_hub/discord.py
    - src/agent_hub/pipeline.py
    - tests/test_filter.py
    - tests/test_discord.py
    - tests/test_pipeline.py

key-decisions:
  - "apply_recency_window runs before relevance_filter to prevent source starvation from first-come-first-cap"
  - "Malformed published_at strings treated as None (conservative pass-through) per T-03-01"
  - "source_breakdown dict replaces source_count int throughout discord.py and pipeline.py"
  - "COVERAGE_THRESHOLD=3: warning fires when <3 sources contribute to a digest"

patterns-established:
  - "Recency window pattern: apply_recency_window(all_items) before any LLM call"
  - "Source breakdown pattern: derive dict[str,int] from filtered items, pass to discord formatter"

requirements-completed:
  - SRC-02

duration: 35min
completed: 2026-04-30
---

# Phase 3: Source Coverage Fix Summary

**48-hour recency window + FILTER_CAP=150 fix source starvation; per-source Discord breakdown with coverage warning when <3 sources contribute**

## Performance

- **Duration:** 35 min
- **Started:** 2026-04-30T00:00:00Z
- **Completed:** 2026-04-30T00:35:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added `apply_recency_window()` to filter.py: excludes items older than 48h, logs per-source exclusions, handles None dates and malformed ISO strings safely
- Raised `FILTER_CAP` from 50 to 150 - eliminates source starvation from the hard cap
- Replaced `source_count: int` with `source_breakdown: dict[str, int]` throughout discord.py and pipeline.py
- Discord success message now shows per-source item counts and appends `⚠️ Only N sources represented` warning when fewer than 3 sources contribute
- All 34 tests pass (23 original + 11 new)

## Task Commits

1. **Task 1: apply_recency_window + FILTER_CAP** - `f44d073` (feat)
2. **Task 2: source_breakdown in discord.py** - `f686856` (feat)
3. **Task 3: wire pipeline.py** - `cc1ca02` (feat)

## Files Created/Modified
- `src/agent_hub/filter.py` - Added RECENCY_HOURS=48, FILTER_CAP=150, apply_recency_window(); fixed items[:50] → items[:FILTER_CAP]
- `src/agent_hub/discord.py` - Added COVERAGE_THRESHOLD=3; format_success/format_digest accept source_breakdown dict
- `src/agent_hub/pipeline.py` - Imports apply_recency_window; removed source_count; added windowed_items + source_breakdown derivation
- `tests/test_filter.py` - 4 new recency window tests
- `tests/test_discord.py` - Updated 5 existing tests; added 4 new coverage tests
- `tests/test_pipeline.py` - Added apply_recency_window mock to all tests; 2 new coverage warning tests

## Decisions Made
- Malformed `published_at` strings pass through (conservative inclusion) rather than crashing the pipeline - per T-03-01 threat mitigation
- `source_count` variable removed entirely from pipeline.py; no backwards compat shim needed

## Deviations from Plan
None - plan executed exactly as written, including T-03-01 try/except guard for malformed dates.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Source coverage fix complete and verified (34/34 tests pass)
- Pipeline ready for live deployment; next digest run will show per-source breakdown in Discord
- Phase 4 can proceed

## Self-Check: PASSED

---
*Phase: 03-source-coverage-fix*
*Completed: 2026-04-30*
