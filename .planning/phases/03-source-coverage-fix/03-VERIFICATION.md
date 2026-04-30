---
phase: 03-source-coverage-fix
verified: 2026-04-30T00:00:00Z
status: human_needed
score: 7/7 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Run the live pipeline against real RSS feeds and inspect the Discord channel"
    expected: "Discord success message shows per-source breakdown line e.g. '(OpenAI Blog: 3, TestingCatalog: 2)' and no 'Only N sources' warning when 3+ sources contribute items"
    why_human: "The recency window and source_breakdown derivation depend on live feed data with real published_at timestamps. Tests mock apply_recency_window with identity pass-through. Only a live run confirms the window actually admits items from multiple sources."
  - test: "Verify Roadmap SC1: confirm diagnostic conclusion is documented (why only OpenAI Blog appeared)"
    expected: "03-CONTEXT.md or 03-REVIEW.md records the diagnosed root cause: the items[:50] cap in filter.py was silently discarding all non-OpenAI-Blog items after the first 50 OpenAI Blog items exhausted the cap"
    why_human: "SC1 requires a documented diagnosis, not just a code fix. The fix is in the code but the written diagnosis lives in planning documents that are outside automated code verification scope."
---

# Phase 3: Source Coverage Fix Verification Report

**Phase Goal:** Ensure the digest consistently draws items from multiple sources, not a single dominant feed.
**Verified:** 2026-04-30T00:00:00Z
**Status:** human_needed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                     | Status     | Evidence                                                                                       |
|----|-------------------------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------------------|
| 1  | Items older than 48 hours are excluded from the relevance filter input                    | ✓ VERIFIED | `apply_recency_window()` in filter.py:36–65 with `RECENCY_HOURS=48`; 4 tests pass             |
| 2  | Items with no published_at date pass through the recency window unchanged                 | ✓ VERIFIED | filter.py:45–47 None-branch; `test_recency_window_passes_none_published_at` passes            |
| 3  | Items from at least 3 distinct sources appear in each digest when available               | ✓ VERIFIED | Recency window prevents per-source starvation; FILTER_CAP=150 removes the 50-item cap         |
| 4  | Discord success message shows per-source breakdown (e.g., OpenAI Blog: 3, TestingCatalog: 2) | ✓ VERIFIED | `format_success()` discord.py:12–37 with `source_breakdown: dict[str, int]`; tests pass       |
| 5  | Discord success message appends warning when fewer than 3 sources contribute              | ✓ VERIFIED | discord.py:33–35 `COVERAGE_THRESHOLD=3` warning; `test_format_success_coverage_warning_below_threshold` passes |
| 6  | Per-source item counts are logged after ingestion and after filter                        | ✓ VERIFIED | pipeline.py:49 `logger.info(f"{source['name']}: {len(items)} items fetched")` and pipeline.py:65 `logger.info(f"{src_name}: {count} items passed filter")` |
| 7  | source_count in status line reflects contributing sources, not configured sources         | ✓ VERIFIED | `source_count` variable removed entirely from pipeline.py; `len(source_breakdown)` used in format_success |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact                          | Expected                                                    | Status     | Details                                                                                   |
|-----------------------------------|-------------------------------------------------------------|------------|------------------------------------------------------------------------------------------|
| `src/agent_hub/filter.py`         | apply_recency_window(), RECENCY_HOURS=48, FILTER_CAP=150    | ✓ VERIFIED | All three present at module level; items[:50] replaced with items[:FILTER_CAP] at line 82 |
| `src/agent_hub/discord.py`        | Updated format_success() and format_digest() with source_breakdown param, COVERAGE_THRESHOLD | ✓ VERIFIED | Both functions accept `source_breakdown: dict[str, int]`; COVERAGE_THRESHOLD=3 at line 10 |
| `src/agent_hub/pipeline.py`       | Wired recency window + source_breakdown derivation          | ✓ VERIFIED | apply_recency_window imported and called; source_breakdown derived and passed to format_digest |

### Key Link Verification

| From                       | To                         | Via                                          | Status     | Details                                                    |
|----------------------------|----------------------------|----------------------------------------------|------------|------------------------------------------------------------|
| `src/agent_hub/pipeline.py` | `src/agent_hub/filter.py`  | `apply_recency_window(all_items)` before `relevance_filter()` | ✓ WIRED | pipeline.py:57 `windowed_items = apply_recency_window(all_items)` then line 58 `relevance_filter(windowed_items, ...)` |
| `src/agent_hub/pipeline.py` | `src/agent_hub/discord.py` | `format_digest(..., source_breakdown)` dict passed | ✓ WIRED | pipeline.py:77 `format_digest(relevant_items, run_num, dt, run_id, raw_count, source_breakdown)` |

### Data-Flow Trace (Level 4)

| Artifact               | Data Variable      | Source                                   | Produces Real Data | Status      |
|------------------------|--------------------|------------------------------------------|--------------------|-------------|
| `discord.py format_success` | source_breakdown | pipeline.py derives from relevant_items after filter | Yes - dict built from actual filtered RawItem.source_name values | ✓ FLOWING |
| `pipeline.py`          | windowed_items     | apply_recency_window(all_items)          | Yes - real cutoff comparison against published_at | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior                      | Command                                            | Result        | Status   |
|-------------------------------|---------------------------------------------------|---------------|----------|
| All 34 tests pass              | `PYTHONPATH=. uv run pytest tests/ -q`           | 34 passed in 0.38s | ✓ PASS |
| source_count removed from pipeline.py | `grep source_count src/agent_hub/pipeline.py` | 0 matches     | ✓ PASS |
| items[:50] removed from filter.py | `grep "items\[:50\]" src/agent_hub/filter.py` | 0 matches     | ✓ PASS |
| RECENCY_HOURS=48 present      | grep RECENCY_HOURS filter.py                     | line 8        | ✓ PASS |
| FILTER_CAP=150 present        | grep FILTER_CAP filter.py                        | line 9        | ✓ PASS |
| COVERAGE_THRESHOLD=3 present  | grep COVERAGE_THRESHOLD discord.py               | line 10       | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description                                                              | Status        | Evidence                                                                                          |
|-------------|-------------|--------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------------|
| SRC-02      | 03-01-PLAN  | "User can define tracked topics covering model releases, AI coding tools, useful new AI tools, and hot trends." | ? NEEDS HUMAN | **Mismatch:** SRC-02 in REQUIREMENTS.md describes topic configurability, NOT source coverage. The phase plan claims SRC-02 completion but the code delivers source starvation fix and per-source logging - not user-configurable topic definitions. The ROADMAP Phase 3 section lists no requirement IDs. This may be a planning artifact labeling error rather than a code gap. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/agent_hub/filter.py` | 81 | Comment says "limit to first 50 items to prevent context/token overflow in Phase 1" - stale comment referring to old cap | ℹ️ Info | Comment is misleading (cap is now 150 via FILTER_CAP), but no functional impact |

### Human Verification Required

#### 1. Live Run Multi-Source Confirmation

**Test:** Run `PYTHONPATH=src uv run --env-file .env python -m agent_hub.pipeline` and check the Discord channel.
**Expected:** Discord message contains a per-source breakdown line like `(OpenAI Blog: 3, TestingCatalog: 2, ...)` with 3 or more distinct sources, and no "⚠️ Only N sources" warning.
**Why human:** All pipeline tests mock `apply_recency_window` with an identity function (`side_effect=lambda x: x`), bypassing the actual recency window. Only a live run with real RSS feeds and real `published_at` timestamps confirms that the window admits multi-source items and that the source_breakdown accurately reflects what Discord receives.

#### 2. SRC-02 Requirement Labeling

**Test:** Confirm whether the plan's claim of SRC-02 completion is intentional or a mislabeling.
**Expected:** Either (a) SRC-02 in REQUIREMENTS.md is updated to match what phase 3 actually delivers, or (b) a new requirement ID is created for source coverage and SRC-02 remains open for a future "topic configurability" feature.
**Why human:** This is a requirements management decision. The code is correct and functional; the mismatch is in how the requirement ID was applied. The ROADMAP Phase 3 section lists no `Requirements:` line - the plan frontmatter added SRC-02 but ROADMAP.md does not confirm this mapping.

### Gaps Summary

No code gaps. All must-have truths are verified in the codebase with passing tests. Two items need human decision before this phase can be marked complete:

1. **Live run validation** - automated tests mock the recency window; a single real pipeline run would confirm the full data flow produces multi-source Discord output.
2. **SRC-02 label audit** - the plan claims SRC-02 but REQUIREMENTS.md defines SRC-02 as topic configurability. This is a planning artifact discrepancy, not a code defect.

---

_Verified: 2026-04-30T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
