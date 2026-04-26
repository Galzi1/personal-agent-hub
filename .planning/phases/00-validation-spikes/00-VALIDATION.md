---
phase: 0
slug: validation-spikes
status: executing
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
updated: 2026-04-24
---

# Phase 0 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual validation (spikes are smoke tests, not automated test suites) |
| **Config file** | config/models.yaml (D-21) |
| **Quick run command** | spikes/.venv/Scripts/python spikes/spike_openrouter.py |
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
| 00-01-01 | 01 | 1 | R1 | T-01 | Discord token in config/microclaw.config.yaml (gitignored) | manual | `microclaw doctor` | — | ✅ green |
| 00-01-02 | 01 | 1 | R1 | — | N/A | manual | `microclaw start` + observe | — | ✅ green |
| 00-02-01 | 02 | 2 | R3 | T-00-02-01 | Secrets file gitignored (Task 1 Step 5) | auto | `python -c "import yaml; yaml.safe_load(open('config/models.yaml'))"` | config/models.yaml | ⬜ pending |
| 00-02-02 | 02 | 2 | R3 | — | N/A | auto | `spikes/.venv/Scripts/python spikes/spike_openrouter.py` | spikes/spike_openrouter.py | ⬜ pending |
| 00-02-03 | 02 | 2 | R3 | T-00-02-02 | Human quality judgment | check | — | — | ⬜ pending |
| 00-03-01 | 03 | 3 | R4 | T-00-05 | N/A | auto | `spikes/.venv/Scripts/python spikes/spike_watchlist.py` | spikes/spike_watchlist.py | ⬜ pending |
| 00-03-02 | 03 | 3 | R4 | — | N/A | check | — | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements — Phase 0 is manual validation, no test framework needed.

*Phase 0 intentionally does not create test infrastructure. Test framework setup belongs in Phase 1.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MicroClaw scheduler fires task | R1 | Requires running MicroClaw runtime and observing execution | Schedule @Personal Agent Hub task, wait 60s, verify it fires |
| Discord message delivery | R1 | Requires checking Discord channel | Send test message via MicroClaw, verify in Discord |
| SQLite persistence | R1 | Requires querying MicroClaw DB | Run agent, then verify via web panel activity view |
| Control panel accessible | R1 | Requires browser access | Open http://127.0.0.1:10961, verify UI loads |
| OpenRouter model quality | R3 | Subjective judgment required | Run 14 tasks, user evaluates each as usable |
| Watchlist coverage | R4 | Requires human judgment of news importance | Compare feed items against known AI news of the week |

---

## Validation Sign-Off

- [x] All tasks have manual verification instructions
- [x] Sampling continuity: each spike has clear pass/fail criteria
- [x] Wave 0: no test infrastructure needed (manual spikes)
- [x] No watch-mode flags
- [x] Feedback latency: N/A (manual)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** verified for Phase 0 execution

