---
phase: 1
slug: ingestion-foundation-run-visibility
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-11
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | none - Wave 0 creates `pyproject.toml` or `pytest.ini` |
| **Quick run command** | `uv run pytest tests/test_run_visibility.py -q` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_run_visibility.py -q`
- **After every plan wave:** Run `uv run pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-VAL-01 | TBD | 0 | SRC-01 | T-01-01 | Fetch only allowlisted watchlist URLs, validate parsed feed payloads, and persist source-attributed raw items from more than one configured source. | integration | `uv run pytest tests/test_ingestion_multisource.py -q` | ❌ W0 | ⬜ pending |
| 01-VAL-02 | TBD | 0 | DGST-04 | T-01-02 | Render only allowed terminal outcomes (`completed_with_candidates`, `completed_no_items`, `failed`) with exact run label, short ID, and trace link in the Discord status output. | integration | `uv run pytest tests/test_run_visibility.py -q` | ❌ W0 | ⬜ pending |
| 01-VAL-03 | TBD | 0 | DGST-04 | T-01-03 | Create a distinct run ID for retry and manual rerun attempts while linking each child run to its parent instead of overwriting prior run state. | unit | `uv run pytest tests/test_run_lineage.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` or `pytest.ini` - test config bootstrap
- [ ] `tests/test_ingestion_multisource.py` - covers SRC-01 multi-source ingestion
- [ ] `tests/test_run_visibility.py` - covers DGST-04 terminal outcomes, run label, and trace-link rendering
- [ ] `tests/test_run_lineage.py` - covers retry/rerun lineage behavior
- [ ] `tests/fixtures/feeds/` - recorded RSS/Atom samples from at least three approved source types

*Framework install: add pytest to the project's Python dev tooling during Wave 0 bootstrap.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Discord status side channel shows start, ingestion complete, and final outcome messages for one real run | DGST-04 | Requires a live Discord channel, real MicroClaw runtime, and provisioned credentials | Configure the allowed status channel, trigger a manual run, confirm the three milestone messages appear with the same run label/short ID lineage |
| Trace link from the final Discord status message lands on the exact run's raw event/log view | DGST-04 | Depends on the live control-panel route and browser navigation rather than a pure unit boundary | Open the trace link from the final status message, verify the page shows the matching run label, timestamps, outcome markers, and related retry/rerun lineage |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
