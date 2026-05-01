---
phase: 4
slug: daily-scheduling
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-01
---

# Phase 4 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (existing) - operational verification primarily uses `sqlite3` queries + filesystem checks, not pytest |
| **Config file** | `pyproject.toml` (pytest section) |
| **Quick run command** | `uv run pytest tests/ -x --tb=short` |
| **Full suite command** | `uv run pytest tests/` |
| **Estimated runtime** | ~5 seconds (existing suite - Phase 4 adds no new pytest tests) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x --tb=short` (regression guard - Phase 4 must not break Phase 1-3 tests)
- **After every plan wave:** Run `uv run pytest tests/` plus operational SQL/filesystem checks defined per-task
- **Before `/gsd-verify-work`:** Full suite green AND scheduled_tasks row exists with correct cron+timezone AND startup `.lnk` exists
- **Max feedback latency:** 10 seconds (pytest + sqlite query)

---

## Per-Task Verification Map

> Populated by gsd-planner. Each task gets a verification row referencing the existing pytest suite (regression) and operational checks (SQL row, file existence, MicroClaw `next_run` value).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD by planner | 01 | 1 | - | - | N/A | operational | `sqlite3 <microclaw.db> "SELECT cron, timezone FROM scheduled_tasks WHERE status='active'"` | ✅ | ⬜ pending |

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No new pytest stubs needed - Phase 4 is operational/runtime config only.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Schedule survives full machine reboot (D-02 / Success Criterion 3) | Phase 4 SC-3 | Real reboot would interrupt the planning/execution session | Proxy: kill MicroClaw → confirm `scheduled_tasks` row persists in DB → relaunch via the same command the `.lnk` invokes → confirm `next_run` is a future Asia/Jerusalem 09:00 timestamp. Real reboot test deferred to user post-execution. |
| Optional 90-second one-shot smoke fire | - | Requires waiting for MicroClaw to actually invoke `run_digest` and post to Discord | Register a one-shot cron 90 seconds in the future, observe `runs` table row appear and Discord message land, then cancel/cleanup. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (N/A - no Wave 0 work)
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
