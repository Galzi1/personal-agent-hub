---
phase: 1
slug: ingestion-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-25
---

# Phase 1 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` - Wave 0 creates this |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| SRC-01-fetch-all | 01-02 | 1 | SRC-01 | - | N/A | unit | `uv run pytest tests/test_ingester.py::test_fetches_all_enabled_sources -x` | ❌ W0 | ⬜ pending |
| SRC-01-parse-items | 01-02 | 1 | SRC-01 | T-feed-tamper | Pydantic validates all RawItem fields; no exec of feed content | unit | `uv run pytest tests/test_ingester.py::test_parses_rss_items -x` | ❌ W0 | ⬜ pending |
| SRC-01-date-fallback | 01-02 | 1 | SRC-01 | - | N/A | unit | `uv run pytest tests/test_ingester.py::test_date_fallback_chain -x` | ❌ W0 | ⬜ pending |
| SRC-01-skip-disabled | 01-02 | 1 | SRC-01 | - | N/A | unit | `uv run pytest tests/test_ingester.py::test_disabled_sources_skipped -x` | ❌ W0 | ⬜ pending |
| DGST-04-success-format | 01-03 | 2 | DGST-04 | - | N/A | unit | `uv run pytest tests/test_discord.py::test_format_success -x` | ❌ W0 | ⬜ pending |
| DGST-04-failure-format | 01-03 | 2 | DGST-04 | - | N/A | unit | `uv run pytest tests/test_discord.py::test_format_failure -x` | ❌ W0 | ⬜ pending |
| DGST-04-no-items-format | 01-03 | 2 | DGST-04 | - | N/A | unit | `uv run pytest tests/test_discord.py::test_format_no_items -x` | ❌ W0 | ⬜ pending |
| DGST-04-run-id-format | 01-03 | 2 | DGST-04 | - | N/A | unit | `uv run pytest tests/test_db.py::test_run_id_format -x` | ❌ W0 | ⬜ pending |
| DGST-04-run-status-success | 01-04 | 3 | DGST-04 | T-sqli | Parameterized queries in all db.py inserts | integration | `uv run pytest tests/test_pipeline.py::test_run_status_success -x` | ❌ W0 | ⬜ pending |
| DGST-04-run-status-failure | 01-04 | 3 | DGST-04 | T-sqli | Parameterized queries in all db.py inserts | integration | `uv run pytest tests/test_pipeline.py::test_run_status_failure -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` - shared fixtures (SAMPLE_RSS, mock_openrouter_pass/fail, tmp SQLite connection)
- [ ] `tests/test_ingester.py` - stubs + implementations for SRC-01 tests
- [ ] `tests/test_filter.py` - relevance filter unit tests with mocked OpenRouter responses
- [ ] `tests/test_db.py` - raw_items insert, runs CRUD, run_id generation tests
- [ ] `tests/test_discord.py` - D-08 format helper tests
- [ ] `tests/test_pipeline.py` - end-to-end smoke (all mocked except SQLite)
- [ ] `pyproject.toml` - uv project with pytest config and all dependencies
- [ ] Framework install: `uv add feedparser==6.0.12 httpx==0.28.1 pyyaml==6.0.3 "pydantic>=2.13.3"` + `uv add --dev "pytest>=9.0.3" "ruff>=0.15.12"`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MicroClaw 08:00 recurring schedule actually fires next day | DGST-04 | Requires waiting 24h; MicroClaw recurring schedule_type unverified in spikes | Register schedule in Plan 01-04, inspect `scheduled_tasks` row, confirm `status` and `next_run` updated after first run |
| Discord status message delivered to correct channel | DGST-04 | Requires live Discord bot token | Run pipeline via MicroClaw, verify message appears in Discord channel |
| OpenRouter API key substituted and live calls succeed | SRC-01 | Human task - real key required | Replace placeholder in `config/microclaw.config.yaml`, run `uv run python -m agent_hub.pipeline`, confirm no 401 errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
