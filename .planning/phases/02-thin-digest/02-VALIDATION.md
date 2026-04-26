---
phase: 2
slug: thin-digest
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-26
---

# Phase 2 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=9.0.3 |
| **Config file** | none (uses pyproject.toml project name only) |
| **Quick run command** | `PYTHONPATH=. uv run pytest tests/ -q` |
| **Full suite command** | `PYTHONPATH=. uv run pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. uv run pytest tests/ -q`
- **After every plan wave:** Run `PYTHONPATH=. uv run pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | D-01, D-02 | - | Title truncated at 80 chars; URLs in angle brackets | unit | `PYTHONPATH=. uv run pytest tests/test_discord.py -q` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | D-09, D-10 | - | Chunking at 1800-char boundary | unit | `PYTHONPATH=. uv run pytest tests/test_discord.py -q` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 0 | D-19 | - | test_format_success / test_format_no_items assertions fixed | unit | `PYTHONPATH=. uv run pytest tests/test_discord.py -q` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | D-11, D-12 | T-RSS-injection | Discord REST API called with correct URL + Bot auth header | unit | `PYTHONPATH=. uv run pytest tests/test_pipeline.py -q` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | D-15 | - | run_digest() returns confirmation string, not formatted message | unit | `PYTHONPATH=. uv run pytest tests/test_pipeline.py -q` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 1 | D-16, D-17 | - | partial status set on mid-stream Discord API failure | unit | `PYTHONPATH=. uv run pytest tests/test_pipeline.py -q` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 1 | D-17 | - | runs table accepts "partial" status string | unit | `PYTHONPATH=. uv run pytest tests/test_db.py -q` | ❌ W0 | ⬜ pending |
| 02-02-05 | 02 | 1 | D-14 | T-double-post | MicroClaw prompt updated; no double-post | manual | See manual verifications below | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_discord.py` - fix `test_format_success` and `test_format_no_items` assertions (add `\nRun ID: ...` line)
- [ ] `tests/test_discord.py` - add `test_format_digest_basic`, `test_format_digest_truncates_title`, `test_format_digest_suppresses_link_preview`, `test_format_digest_splits_chunks`
- [ ] `tests/test_pipeline.py` - add `test_run_digest_posts_to_discord`, `test_run_digest_returns_confirmation`, `test_run_digest_partial_on_discord_failure`; update `test_run_status_success`
- [ ] `tests/test_db.py` - add `test_partial_status_accepted`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MicroClaw does not double-post after pipeline posts directly | D-14 | Requires running MicroClaw's scheduled trigger in the live environment | 1. Update MicroClaw scheduled task prompt. 2. Trigger a manual run. 3. Verify exactly one Discord message batch posted (not two). |
| DISCORD_CHANNEL_ID config key added to microclaw.config.yaml | D-13 | Config file is gitignored; cannot be tested in CI | Check `config/microclaw.config.yaml` contains `channels.discord.channel_id: <id>` after Wave 1 setup task. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
