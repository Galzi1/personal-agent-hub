---
quick_id: 260427-nck
slug: reorder-roadmap-phases-and-organize-into
description: Reorder roadmap phases and organize into milestones
date: 2026-04-27
must_haves:
  truths:
    - ROADMAP.md has 3 milestone sections with correct phase groupings
    - Phase numbering is consistent (0-10) with new order
    - Progress table reflects new phase order and milestone groupings
    - Dependency references updated to match new phase numbers
  artifacts:
    - .planning/ROADMAP.md (updated)
---

# Quick Task 260427-nck: Reorder ROADMAP.md Phases into Milestones

## Task

Restructure `.planning/ROADMAP.md` to:

1. Reorder unresolved phases as:
   - Phase 3: Source Coverage Fix (unchanged)
   - Phase 4: Daily Scheduling (was Phase 7)
   - Phase 5: Self-Healing Missed Digests (was Phase 8)
   - Phase 6: URL Deduplication (was Phase 5)
   - Phase 7: Nanoclaw Capability Spike (was Phase 6)
   - Phase 8: Nanoclaw Migration (was Phase 10)
   - Phase 9: Persistent Searchable Logs (unchanged)
   - Phase 10: Ranked Digest (was Phase 4)

2. Add milestone headers grouping phases:
   - **Milestone 1: MicroClaw AI Digest MVP** - Phases 0–6
   - **Milestone 2: NanoClaw Migration** - Phases 7–8
   - **Milestone 3: Reliability Enhancements** - Phases 9–10

3. Update all `Depends on` references to use new phase numbers.

4. Update progress table to reflect new phase order.

## Tasks

### Task 1: Rewrite ROADMAP.md with milestone structure and new phase numbering

**Files:** `.planning/ROADMAP.md`
**Action:** Edit the file - reorder phases, add milestone sections, update phase numbers, update depends-on references, update progress table.
**Verify:** Phase list matches new order; 3 milestone headers present; progress table has 11 rows (0–10).
**Done:** ROADMAP.md saved with all changes.
