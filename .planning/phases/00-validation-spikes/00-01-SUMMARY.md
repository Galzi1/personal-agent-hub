---
phase: 00-validation-spikes
plan: 01
subsystem: infra
tags: [microclaw, discord, sqlite, windows, serenity, ollama, validation-spike]

requires:
  - phase: 00-validation-spikes
    provides: "Research doc, context doc, plan definition"
provides:
  - "Validated MicroClaw runtime on Windows 11 x86_64 (scheduler, Discord outbound, SQLite persistence, web control panel)"
  - "Confirmed go decision for R1 (MicroClaw sufficiency risk)"
  - "Captured @-mention routing requirement as a Phase 1 design constraint"
  - "Spike results file at .planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md"
affects: [01-ingestion-foundation, phase-1-daily-digest, phase-1.5-thin-digest, any-phase-using-microclaw-runtime]

tech-stack:
  added: ["MicroClaw runtime", "Ollama 0.21.0 client + daemon", "serenity Discord gateway (vendored in MicroClaw)"]
  patterns: ["@-mention routing for bot-as-receiver flows", "config file at repo root, gitignored to prevent secret leaks"]

key-files:
  created:
    - ".gitignore (repo root, excludes microclaw.config.yaml)"
    - ".planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md"
    - ".planning/phases/00-validation-spikes/00-01-SUMMARY.md"
  modified:
    - ".planning/STATE.md (position + last_activity)"
    - ".planning/config.json (auto-chain flag surfaced by GSD)"

key-decisions:
  - "GO decision recorded for MicroClaw on Windows (all 4 smoke tests PASS)"
  - "@-mention routing is the contract Phase 1 must design around for bot-receiver flows"
  - "microclaw.config.yaml stays at repo root but is gitignored (simpler than relocating, safe enough given F3 OpSec note)"

patterns-established:
  - "Secrets-bearing MicroClaw config gitignored rather than relocated - low-friction pattern for solo dev repos"
  - "Bot interaction requires @-mention in shared channels; direct DM path not yet tested but likely alternative"
  - "Validation spikes document *findings*, not just PASS/FAIL, to surface usage contracts for downstream phases"

requirements-completed: []

duration: ~30 min (interactive testing)
completed: 2026-04-23
---

# Phase 00 / Plan 01: MicroClaw Validation Summary

**MicroClaw runtime validated on Windows 11: scheduled tasks fire via LLM-parsed natural language, Discord adapter posts bidirectionally, SQLite persists messages, web control panel surfaces runtime state - all four capabilities green, R1 closed, phase advances to Plan 02 (Ollama evaluation).**

## Performance

- **Duration:** ~30 min interactive testing (plus ~40 min of earlier setup hygiene: gitignore, state sync, push)
- **Started:** 2026-04-23T22:16:30+03:00 (first `microclaw start` log)
- **Completed:** 2026-04-23T22:45:00+03:00 (user GO confirmation)
- **Tasks:** 3 (1 human-action, 1 auto, 1 human-verify)
- **Files created:** 3 (.gitignore, 00-01-SPIKE-RESULTS.md, 00-01-SUMMARY.md)
- **Files modified:** 2 (STATE.md, config.json)

## Accomplishments

- **Test 1 - Scheduled task: PASS.** `@Personal Agent Hub schedule a task...` fired end-to-end: scheduler registered, LLM parsed, Discord posted on time.
- **Test 2 - Discord outbound: PASS.** Direct "send message" request produced correct Discord post.
- **Test 3 - SQLite persistence: PASS.** DB at `C:\Users\galzi\.microclaw\runtime\microclaw.db` holds test-run data; verified indirectly via web panel activity view.
- **Test 4 - Control panel: PASS.** Web UI at `http://127.0.0.1:10961` loaded and surfaced scheduled tasks + message activity.
- **Stretch goal (D-09 visible routing): SKIPPED** - not required for GO; deferred to Phase 1+.
- **Security hygiene:** `microclaw.config.yaml` (contains Discord bot token + Anthropic API key) added to `.gitignore` before any accidental commit; push to origin done with branch upstream set.

## Task Commits

1. **Hygiene: gitignore microclaw.config.yaml** - `10eb975` (chore)
2. **State sync: mark phase 0 executing plan 1 of 3** - `d481f4a` (docs)
3. **Plan 01 artifacts: spike results + summary + final state update** - this commit (docs)

_Note: Plan 01 executed no source-code changes. Its commits are all planning/hygiene artifacts. Task 2's `type="auto"` is about artifact production (the spike results file), not code generation._

## Files Created/Modified

- `.gitignore` - Excludes `microclaw.config.yaml` from git; protects Discord bot token and Anthropic API key from accidental commit.
- `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md` - 4-test results + 4 findings + go/no-go decision.
- `.planning/phases/00-validation-spikes/00-01-SUMMARY.md` - This file.
- `.planning/STATE.md` - Advanced position to Plan 2 of 3, R1 closed out, last_activity updated.

## Decisions Made

- **Keep config at repo root + gitignore** instead of relocating to `$HOME\.microclaw\microclaw.config.yaml`. Rationale: solo-dev ergonomics; gitignore is a sufficient boundary. Flagged in SPIKE-RESULTS F3 as a Phase 1 cleanup option.
- **SQLite verification via web panel** instead of installing `sqlite3` CLI. Rationale: panel reads the DB and surfaces rows, which is stronger evidence of the persistence path working than the CLI would give.
- **SKIPPED stretch goal D-09** (visible multi-agent routing). Rationale: all 4 mandatory tests passed; stretch was optional per plan.

## Deviations from Plan

None - plan executed as written. Task 1's initial @-mention discovery (plain messages silent) briefly looked like a failure but was diagnosed to MicroClaw's routing contract rather than a bug. No auto-fixes invoked.

## Issues Encountered

- **Plain text messages silently dropped by MicroClaw's Discord adapter.** Diagnosed as @-mention requirement (Finding F1 in spike results); resolved by switching to `@Personal Agent Hub <prompt>` format. Documented for Phase 1.
- **`microclaw.config.yaml` with live secrets was sitting untracked in repo root** - would have been committed on any future `git add .`. Closed by adding `.gitignore`.
- **Default web panel password (`helloworld`) logged in plaintext on first start.** Changed immediately after Test 4 login. Flagged as F3 for future Phase 1 hardening if panel is ever exposed beyond localhost.

## User Setup Required

Completed during Task 1:
- Discord bot application created at Developer Portal with `MESSAGE_CONTENT` intent enabled.
- Bot invited to test server "Personal Agent Hub" with Send Messages + Read Message History permissions.
- Ollama daemon installed and running on `127.0.0.1:11434`.
- MicroClaw installed, configured, and doctor-verified (pass=7 miss=3 warn=2 fail=0).

No remaining user setup for Plan 01.

## Next Phase Readiness

**Plan 02 (Ollama model quality evaluation) unblocked.**

- 32 GB RAM confirms the Qwen3 32B track per D-10/D-11 (vs. Gemma 4 27B fallback for 16-31 GB hosts).
- Ollama daemon already running - first action is `ollama pull qwen3:32b` (~20 GB download; can run in background).
- Available RAM was 6.4 GB at setup time; closing background apps before first `ollama run qwen3:32b` is advisable so inference doesn't thrash swap.
- Embedding model `nomic-embed-text` still to pull alongside (per D-12, needed for Phase 2 semantic dedup).

**Tracked risks:**
- R1 (MicroClaw insufficient) - **CLOSED**.
- R3 (Ollama model quality unverified) - actively being addressed by Plan 02.
- R2/R6/R7 - unchanged from prior state.

---
*Phase: 00-validation-spikes*
*Plan: 01*
*Completed: 2026-04-23*
