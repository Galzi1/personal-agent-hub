# MicroClaw Spike Results (Plan 00-01)

**Date:** 2026-04-23
**Phase:** 00-validation-spikes
**Plan:** 01 (MicroClaw 4-capability smoke test)
**Executor:** User + Claude (interactive)

## Environment

| Item | Value |
|------|-------|
| OS | Windows 11 x86_64, WSL=false |
| System RAM | 31,866 MB (~32 GB) |
| Available RAM during setup | ~6.4 GB (will need to free up before Plan 02 Qwen3 32B load) |
| MicroClaw binary | `C:\microclaw\microclaw` |
| MicroClaw data directory | `C:\Users\galzi\.microclaw\` (outside repo, safe) |
| MicroClaw config | `./microclaw.config.yaml` (in repo root, gitignored per commit `10eb975`) |
| SQLite DB | `C:\Users\galzi\.microclaw\runtime\microclaw.db` |
| `microclaw doctor` | pass=7 miss=3 warn=2 fail=0, exit code 0 |
| Ollama client | 0.21.0 (daemon running on `127.0.0.1:11434`) |
| LLM provider | Anthropic (model: `claude-sonnet-4-5-20250929`) |
| Web panel | `http://127.0.0.1:10961` |

## Test Results

### Test 1 - Scheduled task execution - **PASS**

Scheduled "SPIKE-TEST-SCHEDULER" task via `@Personal Agent Hub` mention in Discord `#general` with a 2-minute delay. Task fired end-to-end: scheduler registered it, LLM parsed the natural-language schedule request, Discord adapter posted the resulting message back to the channel when the time arrived.

**Initial failure mode:** Plain-text messages (without @-mention) produced no log output and no bot response. See Finding F1 below.

### Test 2 - Discord message posting - **PASS**

After the @-mention pattern was established, direct "send a message to Discord saying X" request succeeded: bot produced a Discord post with the SPIKE-TEST-DISCORD content in the expected channel.

### Test 3 - SQLite read/write - **PASS**

Database confirmed present and populated at `C:\Users\galzi\.microclaw\runtime\microclaw.db`. Messages from Tests 1 and 2 persisted (verified via web control panel activity view; SQLite CLI not separately installed, but web panel querying the DB acts as indirect confirmation of the persistence path).

### Test 4 - Control panel access - **PASS**

Web UI at `http://127.0.0.1:10961` loaded on first try. Login prompt accepted the temporary password logged during startup (`helloworld`). Panel surfaced: runtime state, scheduled task list (Test 1 task visible and marked completed), and recent message activity (Tests 1 + 2 posts visible).

### Stretch goal - D-09 visible routing - **SKIPPED**

Not attempted. All 4 core tests passed, which is sufficient for the go decision per the plan's success criteria. Visible multi-agent routing remains a Phase 1+ exploration item.

## Findings

### F1 - MicroClaw's Discord adapter requires @-mention invocation

Plain text posted in a channel where the bot has View Channel + Read Message History did NOT reach MicroClaw's event loop (no debug log emission, no response). `@Personal Agent Hub <prompt>` triggered the full pipeline.

**Likely cause:** MicroClaw's router gates on mentions to avoid processing arbitrary channel noise. Confirmed via behavioral testing; not investigated at code level.

**Phase 1 implication:**
- Daily digest flow is unaffected - MicroClaw posts outbound, does not receive.
- Any future interactive Q&A flow (user asks bot a question in a channel) must either: (a) document the @-mention UX contract, (b) use DMs, or (c) investigate whether MicroClaw exposes a prefix-based or channel-whitelisted routing mode.

### F2 - WebSocket `ResetWithoutClosingHandshake` + `Resumed` is normal

Observed at T+~4 minutes into the bot's session. This is Discord's gateway cycling connections, not a MicroClaw bug. Do not add to alert/runbook as a failure signal.

### F3 - Default web panel password is `helloworld` and is logged in plaintext

MicroClaw auto-generates a temporary operator password on first start with no operator configured, and prints it to stdout. On a multi-user host, shared PC, or anywhere logs are shipped, this is an OpSec risk. Mitigation: the warning log line tells you to change it; we did so during Test 4. Flag for Phase 1 if we ever expose the panel beyond localhost.

### F4 - `MESSAGE_CONTENT` intent needs to be toggled ON in the Developer Portal

Already enabled during setup per the pre-flight checklist, so not a blocker - but worth noting: MicroClaw's `requesting MESSAGE_CONTENT intent` log line is declarative, not confirmatory. The Developer Portal toggle is authoritative. A future regression in Portal config would manifest identically to F1 (no log output, no response), so F1 and F4 are adjacent failure modes to diagnose together.

## Security posture (T-00-01, T-00-02)

- **T-00-01 (Info disclosure, config file):** Mitigated. `microclaw.config.yaml` is gitignored (commit `10eb975`). Discord bot token and Anthropic API key remain local-only.
- **T-00-02 (Info disclosure, SQLite DB):** Accepted. `microclaw.db` is inside `C:\Users\galzi\.microclaw\` which is outside the repo. No separate exfil path.

## Overall Assessment

**Go/No-Go: GO**

All 4 mandatory MicroClaw capabilities (scheduler, Discord outbound, SQLite persistence, web control panel) confirmed working on Windows 11 x86_64. No fallback path triggered - D-04 (NanoClaw on WSL2) not needed.

Phase 0 proceeds to Plan 02 (Ollama model quality evaluation, R3 de-risking).

## Notes for Phase 1

1. Bot-as-receiver flows must account for the @-mention requirement (F1).
2. Scheduler poll interval is ~60 seconds; acceptable for daily digest cadence.
3. The `helloworld` default web password is an OpSec wart - if Phase 1 ever exposes the panel beyond localhost, gate that behind an explicit operator-set password.
4. `RUST_LOG=microclaw=debug,serenity=info` is a useful diagnostic verbosity level for future debugging; keep in Phase 1 observability notes.
5. Consider relocating `microclaw.config.yaml` from repo root to `$HOME\.microclaw\microclaw.config.yaml` in a Phase 1 cleanup - cleaner separation than gitignoring a secrets file in the working tree, though current state is safe.
