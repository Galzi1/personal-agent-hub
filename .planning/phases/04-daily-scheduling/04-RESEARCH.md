# Phase 4: Daily Scheduling - Research

**Researched:** 2026-05-01
**Domain:** MicroClaw scheduler API, IANA timezone configuration, Windows reboot persistence (no admin)
**Confidence:** HIGH for MicroClaw schema (verified live DB) and Windows startup folder mechanics; MEDIUM for the natural-language schedule registration flow (cited from MicroClaw README via WebFetch, not exercised in this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scheduler Mechanism**
- D-01: Use MicroClaw's built-in scheduler for the 09:00 daily digest schedule. Windows Task Scheduler is NOT used. The single plan registers the schedule inside MicroClaw.
- D-02: Reboot persistence requires MicroClaw to auto-start on Windows boot. Auto-start mechanism: a shortcut in the Windows startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). No admin rights required; fires on user login.
- D-03: The existing 08:00 MicroClaw schedule from Phase 1 Plan 01-04 must be updated or replaced with the new 09:00 Asia/Jerusalem schedule. One active digest schedule should exist, not two.

**Timezone Configuration**
- D-04: Timezone stored in `config/microclaw.config.yaml` by uncommenting the existing `# Optional timezone override (IANA)` field and setting it to `Asia/Jerusalem`. This is a global MicroClaw timezone, which is acceptable for this single-user, single-timezone setup.
- D-05: No new config file for schedule settings. The existing microclaw.config.yaml field is sufficient and keeps config surface minimal.

### Claude's Discretion
- Exact MicroClaw schedule registration command/syntax (cron expression vs. natural-language time spec - use whatever MicroClaw supports)
- Whether to update the existing 08:00 schedule in-place or delete it and register a new 09:00 one
- Startup shortcut file format (`.bat` launching `microclaw`, `.lnk`, or other Windows startup mechanism)
- How to verify post-reboot persistence in the plan (simulated reboot check vs. documentation of verification steps)

### Deferred Ideas (OUT OF SCOPE)
- None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

No explicit `REQ-XX` IDs are mapped to Phase 4 in `.planning/REQUIREMENTS.md`. The roadmap-level success criteria for Phase 4 are:

| ID (roadmap) | Description | Research Support |
|----|-------------|------------------|
| Phase 4 SC1 | MicroClaw fires `run_digest` at 09:00 Asia/Jerusalem daily | MicroClaw schedule_task tool + 5-field cron `0 9 * * *` + global timezone config (this doc, "MicroClaw Scheduler API") |
| Phase 4 SC2 | Timezone is explicit in config, not hardcoded | `microclaw.config.yaml` has a built-in commented `timezone:` field at line 62 (verified by reading file) |
| Phase 4 SC3 | Schedule survives a machine reboot | MicroClaw persists tasks in `~/.microclaw/runtime/microclaw.db` (verified live DB inspection) + Windows startup folder shortcut launches `microclaw start` on user login (this doc, "Windows Startup Shortcut") |

</phase_requirements>

---

## Summary

MicroClaw v0.1.51 is installed at `C:\microclaw\microclaw.exe` and is the in-scope scheduler per D-01. The runtime DB at `C:\Users\galzi\.microclaw\runtime\microclaw.db` already has a `scheduled_tasks` table with the schema needed for a recurring 09:00 Asia/Jerusalem job - `schedule_type` defaults to `'cron'`, `timezone` is a column on the table itself, and `next_run` / `last_run` are tracked. **Live DB inspection shows zero recurring tasks currently registered** - the only `scheduled_tasks` row is the Plan 00-01 spike one-shot from 2026-04-23, status `completed`. This contradicts the Phase 4 CONTEXT D-03 assumption that a Phase 1 08:00 schedule exists to "update or replace": it does not. The plan author should treat this as a fresh schedule registration, not a modification.

The MicroClaw scheduler is registered through the `schedule_task` built-in tool, which the agent invokes when it interprets a natural-language prompt like "schedule the daily digest every day at 09:00 Asia/Jerusalem". Internally, MicroClaw stores 5 or 6-field cron expressions (5-field is the standard form in OpenClaw docs for the same scheduler family). The scheduler polls every 60 seconds. The global `timezone` field in `microclaw.config.yaml` (currently commented out at line 62) is the single source of truth for cron interpretation when no per-task timezone is provided - which matches D-04. Tasks are persisted in SQLite (WAL mode), so the schedule survives a MicroClaw restart but only if MicroClaw itself is running when 09:00 arrives - hence the startup shortcut.

For reboot persistence (D-02), the Windows user startup folder at `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` accepts both `.lnk` shortcuts and `.bat` files, runs them on user login, and requires no admin rights. There is precedent on this machine: `Ollama.lnk` already lives in that folder (verified by directory listing) and points at `C:\Users\galzi\AppData\Local\Programs\Ollama\ollama app.exe` (verified via WScript.Shell COM). MicroClaw also has a `gateway install` subcommand that registers itself as a Windows Service, but that path requires elevated terminal and is explicitly out-of-scope per D-02.

**Primary recommendation:** (1) Uncomment and set `timezone: "Asia/Jerusalem"` in `config/microclaw.config.yaml` line 62. (2) Register a single recurring task via natural-language prompt to MicroClaw's daily-digest chat, asking it to schedule cron `0 9 * * *` invoking `uv run --project C:/Users/galzi/src/personal-agent-hub python -m agent_hub.pipeline`. (3) Verify the resulting `scheduled_tasks` row has `schedule_type='cron'`, `schedule_value='0 9 * * *'`, `timezone='Asia/Jerusalem'` (or empty if global timezone is honored), and `status='active'` with a future `next_run`. (4) Create a `.lnk` in the user startup folder via PowerShell + WScript.Shell COM that runs `microclaw start --config <abs path>` on login. No admin. Verification of reboot persistence is done by proxy (kill+restart MicroClaw rather than rebooting the machine).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 09:00 daily trigger evaluation | MicroClaw scheduler (Rust) | - | Built-in cron loop polls `scheduled_tasks` every 60s; no Python involvement until fire time |
| Timezone resolution for cron | MicroClaw (config) | - | Global `timezone` in `microclaw.config.yaml` interpreted by croner; Python sees only UTC datetimes |
| `schedule_task` tool invocation | MicroClaw agent loop (LLM) | - | User registers via natural-language @-mention; agent calls the built-in `schedule_task` tool |
| Schedule persistence across MicroClaw restart | SQLite `scheduled_tasks` table | - | WAL-mode SQLite at `~/.microclaw/runtime/microclaw.db`; survives `microclaw start` cycles |
| MicroClaw process auto-start on Windows boot | Windows Explorer (login shell) | `.lnk` in user Startup folder | No admin needed; fires on user login (sufficient for single-user single-machine setup) |
| `run_digest()` execution at fire time | Python sidecar (uv run) | MicroClaw bash tool | Scheduled prompt instructs the agent to run `uv run … python -m agent_hub.pipeline`; Python posts to Discord directly per Phase 2 D-11 |

---

## Standard Stack

### Core
| Library / Component | Version | Purpose | Why Standard |
|---------------------|---------|---------|--------------|
| MicroClaw | v0.1.51 | Scheduler + agent runtime | Already installed at `C:\microclaw\microclaw.exe` [VERIFIED: `microclaw --version`] |
| MicroClaw `scheduled_tasks` table | schema as of v0.1.51 | Persistent cron storage (chat_id, prompt, schedule_type='cron', schedule_value, timezone, next_run, last_run, status) | Built into runtime DB at `~/.microclaw/runtime/microclaw.db` [VERIFIED: `.schema scheduled_tasks`] |
| `schedule_task` built-in tool | v0.1.51 | Tool the agent calls to insert a row into `scheduled_tasks` | Documented in MicroClaw README [CITED: github.com/microclaw/microclaw README via WebFetch] |
| croner cron parser | (bundled in MicroClaw) | Parses 5 or 6-field expressions; honors timezone | Used by the OpenClaw-family scheduler [CITED: docs.openclaw.ai/automation/cron-jobs] |
| Windows user Startup folder | Win11 native | Reboot-persistent auto-launch on user login, no admin | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` [VERIFIED: existing `Ollama.lnk` present] |
| WScript.Shell COM (PowerShell) | Built into Windows | Programmatically create `.lnk` shortcuts | Standard idempotent shortcut creation in Win11 [CITED: Microsoft Learn] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MicroClaw scheduler | Windows Task Scheduler | Rejected by D-01. WTS would survive without MicroClaw running, but adds a second scheduling system to debug. |
| Startup folder `.lnk` | `microclaw gateway install` (Windows Service) | Service runs without user login but requires **elevated terminal** ([CITED: README]). Rejected by D-02 ("no admin rights"). |
| Startup folder `.lnk` | Startup folder `.bat` | `.bat` flashes a console window on every login, ugly UX. `.lnk` with `WindowStyle=7` (minimized) is cleaner. `.bat` is simpler if you don't mind the flash. |
| Asia/Jerusalem in `timezone` field | Per-task `timezone` argument to `schedule_task` | Per-task is more flexible but redundant for single-user/single-tz. D-04 chose global. Note: per-task timezone column exists on `scheduled_tasks` and overrides global if present. |
| Natural-language registration | Direct `INSERT INTO scheduled_tasks` via `sqlite3` | Direct insert bypasses the scheduler's in-memory state - task may not fire until next MicroClaw restart. Avoid. Always go through the agent. |

**No `npm install` or `pip install` step needed for Phase 4** - all components are already present.

---

## Update vs. Replace Decision

**Recommendation: Treat as a fresh schedule registration.** Do not waste plan tasks on "update existing".

**Reasoning:**
1. **Live DB inspection shows zero recurring schedules.** The only row in `scheduled_tasks` is `id=1, schedule_type='once', status='completed'` - the Plan 00-01 spike from 2026-04-23. There is no `daily` or `cron` row to update. [VERIFIED: `SELECT * FROM scheduled_tasks` on 2026-05-01]
2. **Phase 1 SUMMARY confirms the gap.** The Phase 1 SUMMARY (`.planning/phases/01-ingestion-foundation/01-SUMMARY.md`) explicitly says: *"MicroClaw `scheduled_tasks` observed with `schedule_type='once'`. Continuing to monitor if `schedule_type='daily'` is supported natively."* The 08:00 schedule was a Plan 01-04 deliverable in the plan but is not present as evidence in the SUMMARY or the DB. Plan 01-04 also has no SUMMARY artifact.
3. **All 13 runs in the `runs` table were manual.** Their timestamps cluster around two manual sessions (2026-04-25 evening burst of failures+success, then 2026-04-26, 2026-04-30) - none follow an 08:00-daily pattern. [VERIFIED: `SELECT run_id, started_at FROM runs`]

**Plan steps:**
- Skip "find and edit the 08:00 row" entirely.
- The plan still needs a guard: query `scheduled_tasks WHERE status='active'` *before* registering, and if an active digest task already exists from any prior session, cancel it via natural-language `@-mention` ("cancel scheduled task #N") before registering the new 09:00 one. This protects against duplicate schedules even if the live state changes between research and execution.

**Risk if wrong:** If (against current evidence) a hidden active task exists somewhere, registering a second one would result in two daily firings. The pre-registration guard handles this.

---

## Architecture Patterns

### System Architecture Diagram

```
[Windows boot → user login]
        |
        | OS launches startup folder items
        v
[%APPDATA%\…\Startup\Personal-Agent-Hub.lnk]
        | TargetPath: C:\microclaw\microclaw.exe
        | Arguments:  start --config C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml
        | WindowStyle: 7 (minimized)
        v
[microclaw start (long-running process)]
        |
        | Loads config (incl. timezone: "Asia/Jerusalem")
        | Reads scheduled_tasks from microclaw.db
        | Begins 60-second polling loop
        v
[At 09:00 Asia/Jerusalem, scheduler matches cron 0 9 * * *]
        |
        | Inserts task into agent loop with stored prompt
        v
[MicroClaw agent executes prompt in #daily-digest chat]
        |
        | Bash tool: uv run --project … python -m agent_hub.pipeline
        v
[run_digest()] → ingest → filter → SQLite runs row → Discord REST POST
```

**Trace the primary use case from input (cron tick) to output (Discord message) by following the arrows.**

### Pattern 1: Register the Recurring Schedule via Agent Prompt

**What:** Send an `@-mention` to the MicroClaw bot in the existing `#daily-digest` chat. The agent interprets the natural-language request and calls its built-in `schedule_task` tool, which inserts a row into `scheduled_tasks`.

**When to use:** Once, during plan execution. Idempotent - re-registering creates a duplicate, so the plan must guard with a list-and-cancel step.

**Prompt (the plan should send this verbatim to the daily-digest chat):**

```
@Personal Agent Hub Schedule a recurring task to run every day at 09:00 in
the Asia/Jerusalem timezone. Use cron expression "0 9 * * *". The prompt for
the task should be:

"Run the daily AI digest pipeline by executing this command:
 uv run --project C:/Users/galzi/src/personal-agent-hub python -m agent_hub.pipeline
 Then post the result to the #daily-digest channel."

After scheduling, list all active scheduled tasks so I can verify the entry.
```

**Why this works:** Per `[CITED: github.com/microclaw/microclaw]`, MicroClaw's `schedule_task` tool accepts natural-language prompts. The 5-field cron `0 9 * * *` is the canonical form for "9:00 AM daily" in the OpenClaw-family scheduler [CITED: docs.openclaw.ai/automation/cron-jobs]. The chat_id is auto-bound to the originating chat (the daily-digest channel where the @-mention is sent), so the firing prompt will execute and post into that same channel.

**Note on global timezone interpretation:** Once `timezone: "Asia/Jerusalem"` is set in `config/microclaw.config.yaml`, cron expressions without an explicit `--tz` are interpreted in that timezone [CITED: docs.openclaw.ai]. The plan does not need to pass a per-task timezone - the global one suffices and matches D-04. The `timezone` column in the `scheduled_tasks` row may be stored as `'Asia/Jerusalem'` or as empty string `''` (the schema default) - either is acceptable; the plan should document which it observes.

### Pattern 2: Pre-Registration Cancellation Guard

**What:** Before registering, list existing tasks and cancel any active digest schedule.

**When to use:** Always, as the first step in the registration task. Protects against duplicates.

**Prompt:**
```
@Personal Agent Hub List all my active scheduled tasks. For each one whose
prompt mentions "agent_hub.pipeline" or "daily AI digest", cancel it.
```

**Verify:**
```bash
sqlite3 "C:\Users\galzi\.microclaw\runtime\microclaw.db" \
  "SELECT id, schedule_type, schedule_value, timezone, status, prompt
   FROM scheduled_tasks
   WHERE status = 'active' AND prompt LIKE '%agent_hub.pipeline%';"
# Expected: 0 rows BEFORE registration
```

### Pattern 3: Windows Startup Folder `.lnk` (Idempotent Creation via PowerShell)

**What:** Create a `.lnk` shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` that launches `microclaw start --config <path>` minimized on user login.

**When to use:** Once during plan execution. The PowerShell snippet is idempotent - re-running overwrites the same `.lnk` cleanly.

**Code (PowerShell):**
```powershell
# Source: WScript.Shell COM is the Win32 standard for .lnk creation
# [CITED: Microsoft Learn - Windows Script Host COM]

$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "Personal-Agent-Hub.lnk"

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = "C:\microclaw\microclaw.exe"
$lnk.Arguments        = 'start --config "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml"'
$lnk.WorkingDirectory = "C:\Users\galzi\src\personal-agent-hub"
$lnk.WindowStyle      = 7   # 7 = Minimized; 1 = Normal; 3 = Maximized
$lnk.Description      = "Personal Agent Hub - MicroClaw runtime auto-start"
$lnk.Save()

Write-Output "Created: $lnkPath"
```

**Why `.lnk` over `.bat`:**
- `.bat` flashes a console window on every login.
- `.lnk` with `WindowStyle=7` runs minimized.
- `.lnk` is the same mechanism Ollama uses on this machine (proven precedent - `Ollama.lnk` exists in this exact folder, verified 2026-05-01).

**Why user Startup folder over `gateway install`:**
- D-02 requires no admin. `microclaw gateway install` requires elevated terminal [CITED: MicroClaw README via WebFetch].
- User Startup runs on user login, which is sufficient for single-user single-machine.

**Verify the shortcut was created and is well-formed:**
```powershell
$lnkPath = Join-Path ([Environment]::GetFolderPath("Startup")) "Personal-Agent-Hub.lnk"
Test-Path $lnkPath   # expect: True

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
Write-Output "Target:  $($lnk.TargetPath)"
Write-Output "Args:    $($lnk.Arguments)"
Write-Output "WorkDir: $($lnk.WorkingDirectory)"
# Expect: Target = C:\microclaw\microclaw.exe
#         Args   = start --config "..."
```

**Idempotency:** WScript.Shell `CreateShortcut` opens the existing file if it exists; `.Save()` overwrites in place. No append-duplication risk. Re-running the snippet is safe.

### Pattern 4: Reboot Persistence Verification by Proxy

**What:** Verify schedule survives a MicroClaw process restart without actually rebooting the machine.

**Why proxy:** Rebooting Galz's machine during plan execution interrupts the session and is operationally expensive. The two failure modes that a real reboot would catch are:
1. Schedule not persisted to disk → caught by killing+restarting MicroClaw and observing the row reappears.
2. Auto-start shortcut not in startup folder → caught by inspecting the `.lnk` file's existence and contents.

The only failure mode a real reboot catches that the proxy does not is "Windows runs the startup item but `microclaw start` crashes on launch in that environment." This is low-probability and would be caught the first morning the schedule fails to fire (Phase 5 self-healing covers that case, for free).

**Steps:**

1. **Kill the running MicroClaw process** (simulates shutdown):
   ```powershell
   Get-Process microclaw -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

2. **Verify the schedule row is still on disk** (persistence sanity):
   ```bash
   sqlite3 "C:\Users\galzi\.microclaw\runtime\microclaw.db" \
     "SELECT id, schedule_type, schedule_value, timezone, status, next_run
      FROM scheduled_tasks
      WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%';"
   # Expect: exactly 1 row, status='active', schedule_value='0 9 * * *'
   ```

3. **Restart MicroClaw via the same command the startup shortcut will run** (simulates auto-start):
   ```powershell
   Start-Process -FilePath "C:\microclaw\microclaw.exe" `
     -ArgumentList @("start", "--config", "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml") `
     -WindowStyle Minimized
   ```

4. **Confirm MicroClaw loaded the schedule into its in-memory poller**:
   ```bash
   # After ~30 seconds, check that next_run is set to a future time
   sqlite3 "C:\Users\galzi\.microclaw\runtime\microclaw.db" \
     "SELECT next_run FROM scheduled_tasks WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%';"
   # Expect: ISO timestamp in the future (≤24h from now), reflecting the next 09:00 Asia/Jerusalem
   ```

5. **Confirm the startup shortcut is present** (covers reboot mechanics):
   ```powershell
   $lnk = Join-Path ([Environment]::GetFolderPath("Startup")) "Personal-Agent-Hub.lnk"
   Test-Path $lnk   # expect: True
   ```

**Optional (recommended, low-risk smoke test):** Register a *temporary* one-shot task firing 60-90 seconds after registration, with a prompt that posts a short diagnostic line ("smoke test fired at HH:MM") to the daily-digest channel. Confirm the message arrives. Then cancel any leftover state. This proves the end-to-end firing pipeline works in the real environment without waiting until 09:00.

```
@Personal Agent Hub Schedule a one-shot task to fire 90 seconds from now,
with prompt "Post 'Phase 4 smoke test fired at <timestamp>' to #daily-digest".
```

### Anti-Patterns to Avoid

- **Direct `INSERT INTO scheduled_tasks`**: Bypasses MicroClaw's in-memory scheduler state. The row is on disk but won't fire until next process restart. Always register via agent prompt.
- **Hardcoding `Asia/Jerusalem` in Python source**: Regression of Phase 0 D-17. The timezone lives in `config/microclaw.config.yaml`. Python should never see "Asia/Jerusalem" as a string literal.
- **Using `python` directly instead of `uv run --project <path>`**: Without `--project`, the working directory matters and the wrong venv may be picked up. Always pass `--project` with the absolute repo path in the scheduled prompt.
- **`.bat` shortcut without `WindowStyle`**: A `.bat` file in startup will flash a `cmd.exe` console window on every login. If `.bat` must be used, wrap with `start "" /min` and `exit` to dismiss quickly - but `.lnk` is cleaner.
- **Registering the schedule before setting `timezone:` in config**: If the timezone field is still the system default (Windows local time, which on this machine happens to coincide with `Asia/Jerusalem`), the cron will fire at 09:00 - but the run record won't be reproducible if the user later travels or changes regional settings. Always order: (1) config timezone, (2) restart MicroClaw to pick up config, (3) register schedule.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cron parsing / next-fire calculation | Custom datetime arithmetic | MicroClaw's bundled croner | DST transitions, leap seconds, and 6-field semantics are non-trivial; croner handles them |
| Daily timer loop in Python | `while True: sleep until 09:00` | MicroClaw scheduler | Python loop dies on power loss; MicroClaw scheduler is restored from SQLite on restart |
| Auto-start mechanism | Custom Windows boot hook | User Startup folder `.lnk` | Native, no admin, well-documented, idempotent via WScript.Shell |
| `.lnk` byte format | Hand-built binary file | `WScript.Shell.CreateShortcut` (PowerShell COM) | The .lnk format is a Microsoft binary spec; never hand-roll |
| Timezone database in Python | `tzdata` workaround | Don't read TZ in Python | MicroClaw (Rust) handles the cron-side TZ lookup; Python sees only UTC datetimes from `datetime.now(timezone.utc)`. See Pitfall 5. |

**Key insight:** Every component needed already exists on this machine. Phase 4 is a configuration phase, not an implementation phase. The plan should be ~3-4 tasks of about 10-20 minutes each, total.

---

## Runtime State Inventory

> Phase 4 includes a config edit and a schedule registration. No code rename or refactor, but there is non-trivial runtime state.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `scheduled_tasks` table in `~/.microclaw/runtime/microclaw.db`. Currently has 1 row (`id=1`, status `completed`, the Plan 00-01 spike). No active recurring schedule. | Register one new active row via agent prompt. The completed row can stay (it's history). |
| Live service config | None to migrate. The Phase 1 Plan 01-04 prompt was supposed to register an 08:00 schedule, but the DB has no active row matching, so there is nothing to update in place. | Confirm via SQL pre-registration guard (Pattern 2). |
| OS-registered state | **Currently none for this project.** No entry for Personal-Agent-Hub or microclaw in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` (only `Ollama.lnk` exists). | Plan must create `Personal-Agent-Hub.lnk` (Pattern 3). |
| Secrets/env vars | Discord token, OpenRouter key, Discord channel ID - all referenced in `config/microclaw.config.yaml` (gitignored) and `.env`. **No new secrets in Phase 4.** | None. |
| Build artifacts | None. No code changes - Python source and existing tests untouched. The `agent_hub` package is already installed in the uv venv at `.venv/Lib/site-packages/`. | None. |

---

## Common Pitfalls

### Pitfall 1: Phase 1 "08:00 schedule" doesn't actually exist in the DB

**What goes wrong:** Plan author follows D-03 literally, hunts for an 08:00 row to update, doesn't find one, reports "blocked".

**Why it happens:** Plan 01-04 instructed the user to register the schedule via @-mention but produced no SUMMARY confirming registration succeeded. Live DB inspection on 2026-05-01 shows zero active digest schedules.

**How to avoid:** Read this research file. The plan should phrase the task as "ensure exactly one active digest schedule exists at `0 9 * * *` Asia/Jerusalem", not "modify the existing 08:00 schedule". Use the pre-registration guard (Pattern 2) to handle either case.

**Warning signs:** `sqlite3 … "SELECT * FROM scheduled_tasks WHERE status='active'"` returns 0 rows.

### Pitfall 2: Cron 5-field vs 6-field

**What goes wrong:** Author writes `0 0 9 * * *` (6-field with leading seconds) when MicroClaw expected 5-field `0 9 * * *`, or vice versa. The schedule fires at midnight or never.

**Why it happens:** OpenClaw-family scheduler accepts both formats (croner detects field count). MicroClaw README mentions "6-field cron expressions (sec min hour dom month dow)" while OpenClaw docs use 5-field examples. Inconsistent guidance.

**How to avoid:** Use the canonical 5-field form `0 9 * * *`. After registration, query the DB to confirm `schedule_value='0 9 * * *'` (or `'0 0 9 * * *'` if MicroClaw normalized to 6-field). Either is acceptable as long as `next_run` is set to a future ISO timestamp ≤ 24h ahead at the next 09:00 Jerusalem time.

**Warning signs:** `next_run` is more than 24h in the future, or never set, or `last_run` shows the task fired at midnight.

### Pitfall 3: MicroClaw not running when 09:00 arrives

**What goes wrong:** Schedule is registered correctly. Galz reboots. He doesn't manually start MicroClaw. 09:00 passes, no digest.

**Why it happens:** MicroClaw is a foreground process. The startup shortcut is the only thing keeping it alive across reboots.

**How to avoid:** The startup `.lnk` (Pattern 3) is non-optional even though D-02 calls it "persistence". It is the persistence. The plan must verify the shortcut exists and points at the right binary + config.

**Warning signs:** `Get-Process microclaw` returns nothing after a fresh login. `last_run` in `scheduled_tasks` is older than expected.

**Mitigated by:** Phase 5 self-healing will catch a missed 09:00 fire when MicroClaw eventually starts later in the day. But Phase 4 should not lean on Phase 5 - the startup shortcut is the primary control.

### Pitfall 4: Python runs in the wrong venv

**What goes wrong:** Scheduled prompt fires `python -m agent_hub.pipeline` in MicroClaw's working directory, which lacks the project venv. ImportError on `feedparser` or `pydantic`.

**Why it happens:** MicroClaw's `working_dir` is `${MICROCLAW_WORKING_DIR}` (likely `~/.microclaw/working_dir`), not the project root. Running `python` from there picks up system Python.

**How to avoid:** The scheduled prompt must invoke `uv run --project C:/Users/galzi/src/personal-agent-hub python -m agent_hub.pipeline`. The `--project` flag tells uv to use that project's venv regardless of cwd.

**Warning signs:** `runs` table shows `status='failure'` with `error_message` containing `ModuleNotFoundError`.

### Pitfall 5: Python `zoneinfo.ZoneInfo("Asia/Jerusalem")` fails on Windows

**What goes wrong:** Anyone (now or in Phase 5) writes `from zoneinfo import ZoneInfo; ZoneInfo("Asia/Jerusalem")` in Python source - fails with `ZoneInfoNotFoundError: 'No time zone found with key Asia/Jerusalem'`.

**Why it happens:** Windows ships no IANA tz database. CPython's `zoneinfo` falls back to the `tzdata` package, which is not installed in the project's uv venv. [VERIFIED: reproduced 2026-05-01 in this venv]

**How to avoid:** **Don't read the timezone in Python at all.** All datetime persistence is already UTC ISO strings via `datetime.now(timezone.utc)` (verified in `pipeline.py` line 16). The timezone is purely a MicroClaw cron concern. If a future phase needs Python-side timezone arithmetic, add `tzdata` to dependencies (`uv add tzdata`).

**Warning signs:** `ModuleNotFoundError: No module named 'tzdata'` chained from a `ZoneInfoNotFoundError`.

### Pitfall 6: Duplicate 09:00 firings if registration runs twice

**What goes wrong:** Plan re-runs (e.g., human-checkpoint task gets re-executed). Two `scheduled_tasks` rows now exist with the same prompt. Digest posts twice every morning. Two `runs` rows per day. Discord rate limit hit if the digest is large.

**Why it happens:** `schedule_task` tool inserts unconditionally. There's no built-in upsert.

**How to avoid:** Pre-registration guard (Pattern 2) is mandatory. Plan author should also document: *"if you re-run this plan, the cancel-then-register flow restores correctness."*

**Warning signs:** `SELECT COUNT(*) FROM scheduled_tasks WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%'` returns ≥ 2.

### Pitfall 7: Discord rate limits during morning fire

**What goes wrong:** Phase 2 D-09 splits long digests at ~1800 chars. On a high-volume morning (e.g., major model launch day), the digest may post 4-5 chunks. Discord allows 5 messages per 5 seconds per channel. Hitting the wall returns 429s, marks the run as `partial` (Phase 2 D-16/D-17).

**Why it happens:** Phase 2 explicitly deferred rate-limit handling.

**How to avoid (Phase 4):** Nothing. This is Phase 2 territory. Mention it in the plan's risk section so reviewer knows to expect occasional `partial` rows. The schedule itself doesn't make this worse.

**Warning signs:** `runs.status='partial'` with `error_message` mentioning HTTP 429.

---

## Code Examples

### Uncomment timezone in `config/microclaw.config.yaml`

**Current line 62:**
```yaml
# Optional timezone override (IANA), e.g. Asia/Shanghai. Default: system timezone.
```

**After edit:**
```yaml
# Optional timezone override (IANA), e.g. Asia/Shanghai. Default: system timezone.
timezone: "Asia/Jerusalem"
```

The comment line is preserved; the new key is added immediately below it. This matches the file's existing style (comments above keys).

### SQL Verification Queries

**Pre-registration guard:**
```sql
SELECT id, schedule_type, schedule_value, timezone, status
FROM scheduled_tasks
WHERE status = 'active'
  AND prompt LIKE '%agent_hub.pipeline%';
-- Expected before plan runs: 0 rows
```

**Post-registration verification:**
```sql
SELECT id, schedule_type, schedule_value, timezone, status, next_run, prompt
FROM scheduled_tasks
WHERE status = 'active'
  AND prompt LIKE '%agent_hub.pipeline%';
-- Expected: exactly 1 row
--   schedule_type  = 'cron'
--   schedule_value = '0 9 * * *'  (or 6-field equivalent '0 0 9 * * *')
--   timezone       = 'Asia/Jerusalem' or '' (empty - global config used)
--   status         = 'active'
--   next_run       = future ISO timestamp ≤ 24h from now
```

### Diagnostic: confirm next_run is in Asia/Jerusalem 09:00

```bash
# next_run is stored in UTC. Convert mentally: Asia/Jerusalem is UTC+2 (IST) or UTC+3 (IDT).
# 2026-05-01 is in IDT (DST), so 09:00 Jerusalem = 06:00 UTC.
sqlite3 ~/.microclaw/runtime/microclaw.db \
  "SELECT next_run FROM scheduled_tasks WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%';"
# Example expected on 2026-05-01: "2026-05-02T06:00:00+00:00" (next 09:00 IDT)
# In IST (winter): "2026-12-15T07:00:00+00:00" (next 09:00 IST)
```

The plan does not need to special-case DST - croner handles it. Just check the UTC offset from the current Asia/Jerusalem offset (use `https://time.is/Jerusalem` or PowerShell `[TimeZoneInfo]::FindSystemTimeZoneById("Israel Standard Time").GetUtcOffset((Get-Date))`).

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 1 D-15: 08:00 daily run | Phase 4 D-04: 09:00 Asia/Jerusalem | 2026-05-01 (this CONTEXT) | Schedule re-registered at new time; old row (if any) cancelled first |
| Phase 1 RESEARCH speculated `schedule_type='daily'` (Pitfall 1, A1) | Confirmed: `schedule_type='cron'` is the default and the supported recurring type | 2026-05-01 (this research, live DB schema) | Plan uses cron expression `0 9 * * *`, no `daily` keyword |
| MicroClaw assumed running indefinitely | Startup folder `.lnk` makes auto-start explicit | Phase 4 D-02 | New artifact: `Personal-Agent-Hub.lnk` in user startup folder |

**Deprecated/outdated:**
- Phase 1 RESEARCH Pattern 6 fallback ("Windows Task Scheduler") - explicitly out of scope per D-01.
- Phase 1 A1 ("MicroClaw supports recurring `daily` or `cron`") - closed: cron is supported, `daily` is not a real keyword in this scheduler.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | MicroClaw's `schedule_task` tool accepts a natural-language prompt and converts it to cron, per the README at github.com/microclaw/microclaw | "Pattern 1: Register the Recurring Schedule via Agent Prompt" | If the tool requires explicit JSON args, the natural-language prompt may fail; fallback is to instruct the agent more explicitly with the cron expression and timezone as quoted parameters in the prompt. **MEDIUM risk** - mitigated by adding the cron expression `"0 9 * * *"` directly into the prompt text. |
| A2 | The global `timezone` field in `microclaw.config.yaml` is honored by croner when no per-task `--tz` is passed | "Update vs. Replace Decision", "Pattern 1" | If the scheduler ignores global config and falls back to host TZ, behavior is still correct on this Windows machine (host TZ is Asia/Jerusalem) but D-04's "explicit in config" intent is violated. **LOW risk on this machine** - the cron will fire at 09:00 either way. Verify by checking the `timezone` column in the registered row; if it shows the global value, the assumption holds. |
| A3 | `Personal-Agent-Hub.lnk` in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` will fire on every user login on Win11 without admin | "Pattern 3" | **LOW risk** - same folder is in active use on this machine for `Ollama.lnk` (verified 2026-05-01). Microsoft has supported this folder since Windows 95. |
| A4 | Killing and restarting MicroClaw is a sufficient proxy for a real reboot for verifying schedule persistence | "Pattern 4" | **MEDIUM risk** - proxy doesn't catch "Windows runs the .lnk but `microclaw start` immediately exits". Mitigation: the optional 90-second smoke test (Pattern 4 step 6) is a stronger proxy. Galz can also do a real reboot test on his own time after the plan completes; not blocking. |
| A5 | The Plan 01-04 "08:00 schedule" was either never registered or was registered transiently and lost. The current DB state is the truth. | "Update vs. Replace Decision" | **LOW risk** - the plan's pre-registration guard handles either world (existing or absent). |
| A6 | `uv run --project <abs path> python -m agent_hub.pipeline` produces the same behavior as `cd <repo> && uv run python -m agent_hub.pipeline` | "Pitfall 4" | **LOW risk** - `--project` is documented uv behavior. If incorrect, the plan can fall back to having the scheduled prompt `cd` first. |

**These assumptions need user confirmation before execution only if A1 or A2 fail at registration time.** A3-A6 are safe to assume.

---

## Open Questions

1. **What is the chat_id of the existing `#daily-digest` Discord channel?**
   - What we know: `chats` table has 1 row, `chat_id=1494060443155697736`, `channel='discord'`. This is presumably the daily-digest chat.
   - What's unclear: Whether there's only one Discord chat MicroClaw knows about, or whether a "daily-digest" specifically exists separately.
   - Recommendation: Plan task 1 should send the `@-mention` from the existing chat (the only one). MicroClaw will auto-bind chat_id to whatever chat the @-mention is sent from. No special handling needed.

2. **Will MicroClaw normalize 5-field cron `0 9 * * *` to 6-field `0 0 9 * * *` on insert, or store it as-given?**
   - What we know: Both formats are accepted. Storage format not documented.
   - Recommendation: Don't care. Plan verifies `next_run` is set to a future Jerusalem-09:00; the stored expression form is incidental.

3. **Does MicroClaw require `--config` on the startup `.lnk` if the config is in the default location?**
   - What we know: Default config search path is `microclaw.config.yaml` in CWD. `microclaw doctor` (no `--config`) reports "config file not found" when run from outside the project.
   - Recommendation: Always pass `--config` with the absolute path in the `.lnk`. Don't rely on CWD-based config discovery.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| MicroClaw binary | Scheduler + Discord adapter | ✓ | v0.1.51 at `C:\microclaw\microclaw.exe` | none - D-01 mandates it |
| MicroClaw runtime DB | Persistent schedule storage | ✓ | `~/.microclaw/runtime/microclaw.db` (364 KB) | none |
| Project venv (uv) | Python pipeline at fire time | ✓ | `.venv/` in repo root via `uv run --project` | none |
| Windows user Startup folder | Reboot persistence | ✓ | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` (one existing `.lnk`) | none |
| PowerShell with WScript.Shell COM | `.lnk` creation | ✓ | Built into Win11 | `.bat` file (uglier UX) |
| Existing Discord daily-digest chat with bot present | Schedule registration target | ✓ (assumed - 1 chat row in DB, `chat_type='discord'`) | n/a | Plan creates it if missing (5-min manual step) |
| `tzdata` Python package | NOT REQUIRED in Phase 4 | ✗ | n/a | Don't read timezone in Python; let MicroClaw handle it (Pitfall 5) |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None.

**Note:** This phase requires zero new installations. All changes are config edits + a single `.lnk` file + a SQL row inserted via agent prompt.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (existing project venv) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (existing) |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

**Note:** Phase 4 is configuration + scheduler registration, not Python code change. Most validation is **runtime/operational** (SQL queries, file existence checks), not unit tests. The plan should preserve the existing test suite as a regression guard but not add Phase 4-specific Python tests unless a new helper module is introduced.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| Phase 4 SC1 | A `scheduled_tasks` row with `schedule_type='cron'`, `schedule_value='0 9 * * *'` (or 6-field equiv), `status='active'` exists | sql / smoke | `sqlite3 ~/.microclaw/runtime/microclaw.db "SELECT … FROM scheduled_tasks WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%'"` | n/a (runtime check) |
| Phase 4 SC1 | `next_run` is set to a future ISO timestamp within 24h (proves cron parser accepted the expression and timezone) | sql / smoke | same query, check `next_run` column | n/a |
| Phase 4 SC1 | (Optional) End-to-end fire test: a 90-second one-shot task posts a smoke-test message to #daily-digest | manual + DB check | Pattern 4 step 6 - register, wait, observe message, confirm `runs` row inserted with `status='success'` | n/a |
| Phase 4 SC2 | `config/microclaw.config.yaml` contains `timezone: "Asia/Jerusalem"` (uncommented) | static | `grep -E '^timezone:' config/microclaw.config.yaml` | ✓ file exists |
| Phase 4 SC2 | No timezone string literal "Asia/Jerusalem" in Python source | static | `grep -r 'Asia/Jerusalem' src/` returns no matches in `.py` files | ✓ |
| Phase 4 SC3 | `%APPDATA%\…\Startup\Personal-Agent-Hub.lnk` exists with TargetPath = MicroClaw exe and Arguments containing `--config` and the project config path | powershell | Pattern 3 verify snippet | ❌ Wave 0 - file does not yet exist |
| Phase 4 SC3 | Schedule row survives MicroClaw process kill+restart (Pattern 4) | manual / proxy | Steps 1-4 of Pattern 4 | n/a |
| Regression | Existing test suite still green | unit | `uv run pytest tests/ -x -q` | ✓ |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x -q` (regression only - should pass unchanged since no Python code changes)
- **Per wave merge:** Full suite + the 3 SQL smoke checks above
- **Phase gate:** All SQL checks pass + `.lnk` file inspection passes + (optional) end-to-end smoke test posted message in #daily-digest

### Wave 0 Gaps

- [ ] **None for tests** - no new Python module introduced; existing test infrastructure covers the unchanged Python pipeline.
- [ ] `%APPDATA%\…\Startup\Personal-Agent-Hub.lnk` - created in plan execution, not Wave 0.
- [ ] Optional helper script `scripts/install-startup-shortcut.ps1` containing Pattern 3's PowerShell - recommended so the snippet is reproducible and auditable, but not required.

*(If no gaps for unit tests: "Existing test infrastructure covers the unchanged Python pipeline. Phase 4 verification is operational/runtime, not unit-test.")*

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Phase 4 is single-user local config |
| V3 Session Management | No | No sessions |
| V4 Access Control | Yes (file system) | `.lnk` written only to user-scoped Startup folder; never to `%PROGRAMDATA%` (would require admin) |
| V5 Input Validation | No | Cron expression is hardcoded `0 9 * * *`, not user-input |
| V6 Cryptography | No | No crypto |
| V14 Configuration | Yes | `config/microclaw.config.yaml` already gitignored; timezone field has no secrecy concern |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| `.lnk` written to all-users Startup folder by mistake → privileged auto-launch on every user login | Elevation of Privilege | Use `[Environment]::GetFolderPath("Startup")` (per-user) NOT `[Environment]::SpecialFolder::CommonStartup` (all users, requires admin). The PowerShell snippet in Pattern 3 uses the per-user form. |
| Scheduled prompt tampered with to run an arbitrary command at 09:00 | Tampering | The `scheduled_tasks.prompt` column is a TEXT field readable+writable by anyone with file access to `microclaw.db`. Mitigation: file lives in `%USERPROFILE%\.microclaw\runtime\` which is per-user ACL'd. Same threat profile as MicroClaw's existing chat history. |
| Duplicate firings cause duplicate Discord posts (resource exhaustion) | Denial of Service | Pre-registration guard (Pattern 2) + post-registration verification query (Code Examples → "Post-registration verification") |
| `microclaw start` failing on user login leaves the user without a daily digest silently | DoS | Phase 5 self-healing covers missed runs on next start. Phase 4 doesn't need to mitigate further. |
| Startup `.lnk` modified to launch an attacker's binary | Tampering | The `.lnk` is in `%APPDATA%\…\Startup\` which is per-user-writable. An attacker with user-level code execution could replace it - but at that point they already have user code execution. Standard threat model: not Phase 4's problem. |

### Notes

- No new secrets introduced. Discord token and OpenRouter key continue to be environment-resolved into the existing gitignored `microclaw.config.yaml`.
- The `.lnk` file does not contain any secret - only a binary path and CLI arguments. Safe to back up.

---

## Sources

### Primary (HIGH confidence - verified live in this session 2026-05-01)

- **Live MicroClaw runtime DB inspection** at `C:\Users\galzi\.microclaw\runtime\microclaw.db`:
  - `.schema scheduled_tasks` - confirmed schema with `schedule_type DEFAULT 'cron'`, `timezone` column, `next_run`/`last_run`, `status`
  - `SELECT * FROM scheduled_tasks` - confirmed only 1 historical row (Plan 00-01 spike, status `completed`)
  - `.schema chats` - confirmed `chat_id`, `chat_title`, `channel`, `external_chat_id`
  - `SELECT … FROM chats` - confirmed 1 Discord chat (`chat_id=1494060443155697736`)
  - `SELECT … FROM runs` - confirmed all 13 historical runs were manual, no 08:00 cadence
- **`microclaw --version`** - confirmed v0.1.51
- **`microclaw gateway status`** - confirmed gateway service NOT installed (so we know D-02 startup folder path is the only persistence mechanism in play)
- **`microclaw doctor --config <project>`** - confirmed config file is found and platform=windows
- **Direct file read** of `config/microclaw.config.yaml` - confirmed line 62 has the commented `timezone` field ready to uncomment
- **Direct file read** of `src/agent_hub/pipeline.py` - confirmed `if __name__ == "__main__": print(run_digest())` block is present (line 96-98), so `python -m agent_hub.pipeline` works as the schedule's invocation
- **Existing `Ollama.lnk`** in user Startup folder - verified via PowerShell `WScript.Shell`, proves `.lnk` mechanism works on this exact machine without admin
- **Python `zoneinfo` test** - verified `ZoneInfo("Asia/Jerusalem")` raises `ZoneInfoNotFoundError` (Pitfall 5)

### Secondary (MEDIUM confidence - cited from official-ish sources, not exercised)

- **github.com/microclaw/microclaw README** (via WebFetch) - `schedule_task` tool, natural-language prompts, 60s polling, 6-field cron, "Windows uses a native Windows Service hosted directly by `microclaw.exe`. Run gateway service commands from an elevated terminal."
- **docs.openclaw.ai/automation/cron-jobs** (via WebFetch) - 5-field cron form `0 9 * * *`, `--tz` flag for timezone, "Cron without `--tz` uses the gateway host timezone", `openclaw cron list/show/remove` commands. Note: OpenClaw is a related but distinct product; MicroClaw shares the croner-based scheduler family but has natural-language prompt-based registration instead of a CLI.

### Tertiary (LOW confidence - community / inference)

- WebSearch summarization of OpenClaw blog posts (mindstudio.ai, lumadock.com, stack-junkie.com) - referenced for cross-checking that 5-field cron is the canonical form. Treat as secondary corroboration only.

---

## Metadata

**Confidence breakdown:**
- MicroClaw schedule DB schema: **HIGH** - directly inspected
- Existing schedule state in DB: **HIGH** - directly inspected; no active recurring task
- `.lnk` startup mechanism: **HIGH** - Ollama.lnk precedent on same machine
- `schedule_task` tool natural-language registration: **MEDIUM** - README-cited, not run end-to-end in this session. Mitigation: include cron expression and timezone explicitly in the registration prompt so even a less-capable interpretation produces the right SQL row.
- Cron field count (5 vs 6): **MEDIUM** - both forms documented as accepted; plan should canonicalize to 5-field and verify `next_run` post-insert rather than relying on the stored expression form.
- Python timezone landmine: **HIGH** - reproduced live (Pitfall 5)
- Reboot persistence proxy verification: **MEDIUM** - kill+restart catches most failure modes; full reboot left to Galz's discretion post-plan

**Research date:** 2026-05-01
**Valid until:** 2026-05-31 (30 days - MicroClaw v0.1.51 stable; only risk is a MicroClaw upgrade changing the schedule_task tool's behavior)
