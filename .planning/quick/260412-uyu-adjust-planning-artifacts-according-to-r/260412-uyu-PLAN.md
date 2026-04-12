---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/ROADMAP.md
  - .planning/PROJECT.md
  - .planning/STATE.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "ROADMAP.md contains a Phase 0 validation spikes block with R1, R3, R4 spikes"
    - "ROADMAP.md contains a thin digest milestone reference (Phase 1.5 or within Phase 1)"
    - "ROADMAP.md contains a risk register reference section at the bottom"
    - "PROJECT.md Key Decisions table includes risk review entries"
    - "PROJECT.md has a Risks section referencing RISK-REVIEW.md"
    - "PROJECT.md Constraints mention planning-to-execution ratio guard"
    - "STATE.md reflects validation spikes should precede Phase 1 implementation"
    - "STATE.md has tracked risks in Accumulated Context"
---

<objective>
Update ROADMAP.md, PROJECT.md, and STATE.md to incorporate the 5 recommended actions and top risks from the risk review (.planning/RISK-REVIEW.md).

Purpose: Align planning artifacts with risk review findings so execution proceeds with awareness of critical risks (R1, R2, R3) and validation spikes are visible in the roadmap.
Output: Three updated planning documents with risk-informed additions.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/RISK-REVIEW.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update ROADMAP.md with Phase 0, thin digest milestone, and risk register reference</name>
  <files>.planning/ROADMAP.md</files>
  <action>
Read .planning/ROADMAP.md. Make THREE additions while preserving all existing content:

1. **Add Phase 0: Validation Spikes** — Insert a new phase BEFORE Phase 1 in the Phases list and Phase Details section. Structure:
   - Phase 0 checkbox entry in the Phases list: `- [ ] **Phase 0: Validation Spikes** - De-risk critical assumptions before committing to implementation.`
   - Phase Details block:
     - Goal: Validate that MicroClaw, Ollama, and the starter watchlist are sufficient for v1 before writing application code.
     - Depends on: Nothing
     - Requirements: None (risk mitigation, not feature delivery)
     - Success Criteria: (1) MicroClaw spike confirms scheduler, Discord posting, and SQLite persistence work on Windows (R1). (2) Ollama model evaluation on 10-20 representative ranking/summarization tasks meets minimum quality bar (R3). (3) Watchlist backtest against one real week of AI news shows acceptable coverage (R4).
     - Plans: TBD

2. **Add Phase 1.5: Thin Digest** — Insert between Phase 1 and Phase 2 in both the Phases list and Phase Details. Use decimal numbering per the existing convention. Structure:
   - Phase 1.5 checkbox entry: `- [ ] **Phase 1.5: Thin Digest** - Deliver a minimal daily digest to Discord to close the time-to-value gap.`
   - Phase Details block:
     - Goal: Post a simple formatted list of ingested items to Discord daily, giving the user a tangible artifact before dedup and ranking exist.
     - Depends on: Phase 1
     - Requirements: None (risk mitigation for R2 — early value delivery)
     - Success Criteria: (1) User receives a daily Discord message listing ingested items with source and title. (2) End-to-end pipeline (schedule, ingest, format, deliver) is validated.
     - Plans: TBD

3. **Add a Risk Register Reference section** at the bottom of the file (after Progress table):
   ```
   ## Risk Register

   See `.planning/RISK-REVIEW.md` for the full risk register (R1-R10), assumption analysis, and recommended actions.

   **Top risks informing roadmap structure:**
   - **R1 (Critical):** MicroClaw proves insufficient — mitigated by Phase 0 validation spike
   - **R2 (High):** Long time to first useful digest — mitigated by Phase 1.5 thin digest milestone
   - **R3 (High):** Local Ollama model quality insufficient — mitigated by Phase 0 evaluation spike
   ```

4. **Update the Progress table** to include Phase 0 and Phase 1.5 rows (both 0/TBD, Not started).

5. **Update the Execution Order** line to: `Phases execute in numeric order: 0 → 1 → 1.5 → 2 → 3 → 4`

6. **Update total count** — the Phases list should now show 6 phases (0, 1, 1.5, 2, 3, 4).
  </action>
  <verify>
    <automated>grep -c "Phase 0" .planning/ROADMAP.md && grep -c "Phase 1.5" .planning/ROADMAP.md && grep -c "Risk Register" .planning/ROADMAP.md</automated>
  </verify>
  <done>ROADMAP.md contains Phase 0 with three validation spikes, Phase 1.5 thin digest milestone, risk register reference section, and updated progress table — all existing content preserved.</done>
</task>

<task type="auto">
  <name>Task 2: Update PROJECT.md with risk review decisions, risks section, and constraint update</name>
  <files>.planning/PROJECT.md</files>
  <action>
Read .planning/PROJECT.md. Make THREE additions while preserving all existing content:

1. **Add rows to the Key Decisions table** (append after existing rows):

| Run validation spikes before Phase 1 implementation | Risk review identified MicroClaw (R1), Ollama quality (R3), and watchlist coverage (R4) as testable unknowns that should be resolved early | Phase 0 added to roadmap |
| Add thin digest milestone after Phase 1 | Risk review identified motivation attrition from long time to first useful digest (R2) as a high risk | Phase 1.5 added to roadmap |
| Enforce planning-to-execution ratio guard | Risk review identified over-planning relative to execution (R6) — no new planning artifacts until current phase first plan is implemented and passing | Active constraint |

2. **Add a new section "Risks"** after the Key Decisions section (before Evolution):
   ```
   ## Risks

   A formal risk review was conducted on 2026-04-12. The full risk register with 10 identified risks (R1-R10), assumption analysis, and recommended actions is maintained in `.planning/RISK-REVIEW.md`.

   **Critical risks actively mitigated by roadmap structure:**
   - **R1:** MicroClaw as single point of failure — Phase 0 validation spike
   - **R2:** Long time to first useful digest — Phase 1.5 thin digest milestone
   - **R3:** Local model quality uncertainty — Phase 0 Ollama evaluation spike
   ```

3. **Update Constraints section** — append a new bullet:
   - **Planning Guard**: No new planning artifacts until the current phase's first plan is implemented and passing tests (R6 mitigation).

4. **Update the "Last updated" line** at the bottom to: `*Last updated: 2026-04-12 after risk review integration*`
  </action>
  <verify>
    <automated>grep -c "Risks" .planning/PROJECT.md && grep -c "Planning Guard" .planning/PROJECT.md && grep -c "validation spikes" .planning/PROJECT.md</automated>
  </verify>
  <done>PROJECT.md has three new Key Decisions rows for risk review actions, a Risks section referencing RISK-REVIEW.md, and an updated Planning Guard constraint.</done>
</task>

<task type="auto">
  <name>Task 3: Update STATE.md with risk awareness and adjusted current position</name>
  <files>.planning/STATE.md</files>
  <action>
Read .planning/STATE.md. Make THREE updates while preserving all existing content:

1. **Update frontmatter:**
   - Change `stopped_at` to: `Risk review integrated; validation spikes precede Phase 1`
   - Change `last_updated` to current date
   - Change `last_activity` to: `2026-04-12 — Risk review findings integrated into planning artifacts`
   - Change `total_phases` to: `6` (added Phase 0 and Phase 1.5)

2. **Update "Current Position" section:**
   - Change "Phase: 1 of 4" to "Phase: 0 of 6 (Validation Spikes)"
   - Change "Status: Ready to plan" to "Status: Ready to plan Phase 0 validation spikes"
   - Change "Last activity" to: `2026-04-12 — Risk review findings integrated into planning artifacts`
   - Add a note below: `Note: Phase 0 validation spikes (MicroClaw, Ollama quality, watchlist backtest) should complete before Phase 1 implementation begins. See .planning/RISK-REVIEW.md.`

3. **Add "Tracked Risks" subsection** inside Accumulated Context (after Decisions, before Pending Todos):
   ```
   ### Tracked Risks

   Risk review conducted 2026-04-12. Full register: `.planning/RISK-REVIEW.md`

   Top risks actively tracked:
   - **R1 (Critical):** MicroClaw may prove insufficient — validation spike in Phase 0
   - **R2 (High):** Long time to first useful digest — thin digest milestone in Phase 1.5
   - **R3 (High):** Ollama model quality unverified — evaluation spike in Phase 0

   Additional concerns:
   - **R6 (Medium):** Over-planning vs execution — planning-to-execution ratio guard active
   - **R7 (Medium):** Windows-specific runtime issues — covered by Phase 0 MicroClaw spike
   ```

4. **Update Blockers/Concerns** — add two items:
   - MicroClaw validation spike must pass before Phase 1 implementation (R1).
   - Ollama model quality must meet minimum thresholds before Phase 2 planning (R3).
  </action>
  <verify>
    <automated>grep -c "Tracked Risks" .planning/STATE.md && grep -c "Phase 0" .planning/STATE.md && grep -c "R1" .planning/STATE.md</automated>
  </verify>
  <done>STATE.md reflects Phase 0 as current position, has Tracked Risks section with top 5 risks, and updated Blockers/Concerns with R1 and R3 gates.</done>
</task>

</tasks>

<verification>
All three documents updated with risk review findings:
- `grep "Phase 0" .planning/ROADMAP.md .planning/STATE.md` returns matches in both files
- `grep "RISK-REVIEW.md" .planning/ROADMAP.md .planning/PROJECT.md .planning/STATE.md` returns matches in all three files
- `grep "Planning Guard" .planning/PROJECT.md` returns a match
- No existing content was removed (only additions)
</verification>

<success_criteria>
1. ROADMAP.md has Phase 0 (validation spikes) and Phase 1.5 (thin digest) with full Phase Details blocks
2. PROJECT.md has three new Key Decisions, a Risks section, and the Planning Guard constraint
3. STATE.md reflects Phase 0 as current position with Tracked Risks in Accumulated Context
4. All three documents reference .planning/RISK-REVIEW.md rather than duplicating the risk register
5. No existing content was removed or replaced
</success_criteria>

<output>
After completion, create `.planning/quick/260412-uyu-adjust-planning-artifacts-according-to-r/260412-uyu-SUMMARY.md`
</output>
