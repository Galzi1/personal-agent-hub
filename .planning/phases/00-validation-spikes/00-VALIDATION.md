---
phase: 0
slug: validation-spikes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-13
---

# Phase 0 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual validation (spikes are smoke tests, not automated test suites) |
| **Config file** | None — Phase 0 does not establish test infrastructure |
| **Quick run command** | N/A |
| **Full suite command** | N/A |
| **Estimated runtime** | ~30 minutes per spike (manual verification) |

---

## Sampling Rate

- **After every task commit:** Manual verification of spike outcome
- **After every plan wave:** Review go/no-go decisions for completed spikes
- **Before `/gsd-verify-work`:** All 3 spike go/no-go decisions recorded
- **Max feedback latency:** N/A (manual validation)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 00-01-01 | 01 | 1 | R1 | — | Discord token stored in MicroClaw config, not git | manual | `microclaw doctor` | N/A | ⬜ pending |
| 00-01-02 | 01 | 1 | R1 | — | N/A | manual | `microclaw start` + observe | N/A | ⬜ pending |
| 00-02-01 | 02 | 2 | R3 | — | N/A | manual | `ollama run qwen3:32b` | N/A | ⬜ pending |
| 00-03-01 | 03 | 3 | R4 | — | N/A | semi-auto | `python spike_watchlist.py` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements — Phase 0 is manual validation, no test framework needed.

*Phase 0 intentionally does not create test infrastructure. Test framework setup belongs in Phase 1.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MicroClaw scheduler fires task | R1 | Requires running MicroClaw runtime and observing execution | Schedule a task, wait 60s, verify it fires |
| Discord message delivery | R1 | Requires checking Discord channel | Send test message via MicroClaw, verify in Discord |
| SQLite persistence | R1 | Requires querying MicroClaw DB | Run agent, then `sqlite3 microclaw.db ".tables"` |
| Control panel accessible | R1 | Requires browser access | Open http://127.0.0.1:10961, verify UI loads |
| Ollama model quality | R3 | Subjective judgment required | Run 10-15 tasks, user evaluates each as pass/fail |
| Watchlist coverage | R4 | Requires human judgment of news importance | Compare feed items against known AI news of the week |

---

## Validation Sign-Off

- [ ] All tasks have manual verification instructions
- [ ] Sampling continuity: each spike has clear pass/fail criteria
- [ ] Wave 0: no test infrastructure needed (manual spikes)
- [ ] No watch-mode flags
- [ ] Feedback latency: N/A (manual)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
