# Phase 4: Daily Scheduling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-01
**Phase:** 4-daily-scheduling
**Areas discussed:** Scheduler mechanism, Timezone config placement

---

## Scheduler Mechanism

### Does MicroClaw auto-start on Windows boot?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, auto-starts on boot | MicroClaw scheduler handles everything - update existing 08:00 schedule. Reboot survival guaranteed if startup app. | |
| No, launched manually | Would require Windows Task Scheduler to fire run_digest directly. | |
| Not sure | Verify during plan execution and pick mechanism then. | ✓ |

**User's choice:** Not sure
**Notes:** User doesn't know current MicroClaw startup status. Decision: prefer MicroClaw scheduler approach and configure auto-start rather than switching to Windows Task Scheduler.

---

### Preferred scheduling approach for reboot persistence

| Option | Description | Selected |
|--------|-------------|----------|
| Windows Task Scheduler | OS-native, always survives reboots. Bypasses MicroClaw control plane. | |
| MicroClaw scheduler + make it auto-start | Configure MicroClaw as Windows startup app AND set 09:00 schedule. Keeps everything inside MicroClaw. | ✓ |
| Both - MicroClaw + Task Scheduler fallback | Redundant dual-scheduler approach. Phase 5 handles duplicate-run detection. | |

**User's choice:** MicroClaw scheduler + make it auto-start
**Notes:** User prefers keeping scheduling inside MicroClaw's control plane. Auto-start will be configured as part of this phase.

---

### MicroClaw auto-start mechanism on Windows

| Option | Description | Selected |
|--------|-------------|----------|
| Windows startup folder shortcut | Drop shortcut in %APPDATA%\Startup. No admin rights. Runs on user login. | ✓ |
| Task Scheduler auto-start | Use Task Scheduler to launch MicroClaw. More configurable but more complex. | |
| Leave to Claude's discretion | Planner picks appropriate auto-start mechanism. | |

**User's choice:** Windows startup folder shortcut
**Notes:** No admin rights needed. Fires on user login. Straightforward approach.

---

## Timezone Config Placement

| Option | Description | Selected |
|--------|-------------|----------|
| microclaw.config.yaml global timezone | Uncomment existing `# Optional timezone override (IANA)` field, set Asia/Jerusalem. | ✓ |
| New digest-specific config key | Add schedule_timezone to config/schedule.yaml (new file). More granular. | |

**User's choice:** microclaw.config.yaml global timezone
**Notes:** Single-user, single-timezone setup - global MicroClaw timezone is appropriate. Reuses the existing commented-out field rather than adding a new config file.

---

## Claude's Discretion

- Exact MicroClaw schedule registration command/syntax
- Whether to update or delete-and-recreate the existing 08:00 schedule from Phase 1
- Startup shortcut file format (.bat vs .lnk vs other)
- How to verify post-reboot persistence in the plan

## Deferred Ideas

None - discussion stayed within phase scope.
