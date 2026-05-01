# Phase 4: Daily Scheduling - Context

**Gathered:** 2026-05-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Configure automatic daily execution of `run_digest` at 09:00 Asia/Jerusalem via MicroClaw's built-in scheduler, with timezone explicitly stored in config and schedule surviving machine reboots via a Windows startup shortcut.

**In scope:**
- Update the existing 08:00 MicroClaw schedule (from Phase 1) to 09:00 Asia/Jerusalem
- Set `timezone: "Asia/Jerusalem"` in `config/microclaw.config.yaml` (uncomment existing field)
- Create a Windows startup folder shortcut so MicroClaw auto-starts on user login
- Verify reboot persistence (schedule survives after machine restart)

**Out of scope:**
- Windows Task Scheduler (MicroClaw scheduler is the chosen mechanism)
- Missed-run catch-up (Phase 5)
- URL deduplication (Phase 6)

</domain>

<decisions>
## Implementation Decisions

### Scheduler Mechanism

- **D-01:** Use MicroClaw's built-in scheduler for the 09:00 daily digest schedule. Windows Task Scheduler is NOT used. The single plan registers the schedule inside MicroClaw.
- **D-02:** Reboot persistence requires MicroClaw to auto-start on Windows boot. Auto-start mechanism: a shortcut in the Windows startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). No admin rights required; fires on user login.
- **D-03:** The existing 08:00 MicroClaw schedule from Phase 1 Plan 01-04 must be updated or replaced with the new 09:00 Asia/Jerusalem schedule. One active digest schedule should exist, not two.

### Timezone Configuration

- **D-04:** Timezone stored in `config/microclaw.config.yaml` by uncommenting the existing `# Optional timezone override (IANA)` field and setting it to `Asia/Jerusalem`. This is a global MicroClaw timezone, which is acceptable for this single-user, single-timezone setup.
- **D-05:** No new config file for schedule settings. The existing microclaw.config.yaml field is sufficient and keeps config surface minimal.

### Claude's Discretion

- Exact MicroClaw schedule registration command/syntax (cron expression vs. natural-language time spec - use whatever MicroClaw supports)
- Whether to update the existing 08:00 schedule in-place or delete it and register a new 09:00 one
- Startup shortcut file format (`.bat` launching `microclaw`, `.lnk`, or other Windows startup mechanism)
- How to verify post-reboot persistence in the plan (simulated reboot check vs. documentation of verification steps)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Prior Phase Decisions (locked)

- `.planning/phases/03-source-coverage-fix/03-CONTEXT.md` - Phase 3 locked decisions. Most recent prior context.
- `.planning/phases/02-thin-digest/02-CONTEXT.md` - Phase 2 locked decisions. Critical: D-11 (direct Discord REST API posting).
- `.planning/phases/01-ingestion-foundation/01-CONTEXT.md` - Phase 1 locked decisions. Critical: D-08 (Discord message formats, must not break), D-14 (`runs` table schema used by Phase 5 self-healing).
- `.planning/phases/00-validation-spikes/00-CONTEXT.md` - Phase 0 locked decisions. Critical: D-17 (no hardcoded values - timezone must stay in config).

### Project Requirements

- `.planning/PROJECT.md` - Core constraints: Windows-first, planning guard, single-user.
- `.planning/REQUIREMENTS.md` - Active requirements list.

### Existing Config Files (read before planning)

- `config/microclaw.config.yaml` - Contains the commented-out `timezone` field to uncomment. Also scheduler, channels, and LLM provider config.
- `src/agent_hub/pipeline.py` - Contains `if __name__ == "__main__": print(run_digest())` - the entry point MicroClaw's schedule calls.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/agent_hub/pipeline.py` - `run_digest()` is the function the scheduler must invoke. Already supports direct execution via `__main__` block. No changes to Python code expected for Phase 4.

### Established Patterns

- **No hardcoded values** (Phase 0 D-17): Timezone lives in config, not in Python source or MicroClaw schedule command.
- **Config in `config/` directory**: All project-level config lives in `config/`. The microclaw.config.yaml path is `config/microclaw.config.yaml` relative to project root.

### Integration Points

- MicroClaw scheduler → `python -m src.agent_hub.pipeline` (or equivalent invocation) - must be verified to fire at 09:00 Asia/Jerusalem.
- MicroClaw startup shortcut → references the MicroClaw executable or launch script. The shortcut must point to wherever `microclaw` is installed.
- `runs` table (already exists from Phase 1) - every digest run is recorded here. Phase 5 self-healing will read this table to detect missed runs; Phase 4 must not change the schema.

</code_context>

<specifics>
## Specific Ideas

- Startup shortcut goes in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` - no admin rights, fires on user login.
- Schedule time: `09:00` Asia/Jerusalem (not 08:00 which was Phase 1's placeholder). The 1-hour shift makes the deadline explicit in the config alongside the timezone.

</specifics>

<deferred>
## Deferred Ideas

- None - discussion stayed within phase scope.

</deferred>

---

*Phase: 4-Daily-Scheduling*
*Context gathered: 2026-05-01*
