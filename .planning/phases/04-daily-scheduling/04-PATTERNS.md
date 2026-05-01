# Phase 4: Daily Scheduling - Pattern Map

**Mapped:** 2026-05-01
**Files analyzed:** 3 (1 modify, 1 create-outside-repo, 1 optional create-in-repo)
**Analogs found:** 1 / 3 strong analogs in this codebase. Phase 4 is overwhelmingly a configuration/runtime phase. The PowerShell `.lnk` work has no in-repo analog (no project-authored `.ps1`/`.bat` exists today) but has a same-machine OS analog (`Ollama.lnk`). The MicroClaw schedule registration is not a "file" at all - it is a runtime SQL row inserted via natural-language `@-mention`.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `config/microclaw.config.yaml` | config | static | `config/microclaw.config.yaml` (self - line 62 has commented `timezone` field) | exact - modify in place, uncomment one line |
| `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Personal-Agent-Hub.lnk` | startup-shortcut (Windows binary) | OS-event (login fires) | `%APPDATA%\…\Startup\Ollama.lnk` (same folder on same machine, verified 2026-05-01 in 04-RESEARCH.md) | OS-precedent - identical mechanism, different target |
| `scripts/install-startup-shortcut.ps1` (OPTIONAL - planner's discretion) | utility-script | one-shot OS-side-effect | None in repo. `scripts/` contains only the third-party `git-filter-repo.py` (not a style analog). | NEW - no in-repo analog |

**Not a file at all (recorded here so the planner does not look for one):**

| Artifact | Where it lives | Created by | Why no file analog |
|----------|----------------|-----------|--------------------|
| `scheduled_tasks` row (`schedule_type='cron'`, `schedule_value='0 9 * * *'`, `status='active'`) | `C:\Users\galzi\.microclaw\runtime\microclaw.db` (SQLite, MicroClaw-managed) | The MicroClaw agent invoking its built-in `schedule_task` tool in response to an `@-mention` prompt sent in the `#daily-digest` Discord channel | This row is runtime state owned by MicroClaw, not a repo artifact. No file is created or modified in the project tree. The "pattern" is the prompt text, captured in 04-RESEARCH.md "Pattern 1". |

---

## Pattern Assignments

### `config/microclaw.config.yaml` (config, static) - MODIFY

**Analog:** self. The file already contains the `timezone` placeholder as a comment on line 62 (verified 2026-05-01 in `04-RESEARCH.md` and via direct `Read` of the file).

**Current state** (verified by reading the file 2026-05-01):
```yaml
60: data_dir: "${MICROCLAW_DATA_DIR}"
61: working_dir: "${MICROCLAW_WORKING_DIR}"
62: # Optional timezone override (IANA), e.g. Asia/Shanghai. Default: system timezone.
63: high_risk_tool_user_confirmation_required: true
```

**Change pattern - uncomment + add the active key directly below the comment** (preserves the documentation comment as a sibling, matching the file's own existing style of "comment line above key" - see lines 32 / 33 (`# LLM provider …` / `llm_provider: "anthropic"`) and lines 36 / 37 (`# Model name …` / `model: "..."`):
```yaml
60: data_dir: "${MICROCLAW_DATA_DIR}"
61: working_dir: "${MICROCLAW_WORKING_DIR}"
62: # Optional timezone override (IANA), e.g. Asia/Shanghai. Default: system timezone.
63: timezone: "Asia/Jerusalem"
64: high_risk_tool_user_confirmation_required: true
```

**Style notes copied from this file's own existing patterns:**
- Use double-quoted string for the IANA value (matches `llm_provider: "anthropic"`, `model: "claude-sonnet-4-5-20250929"`).
- Keep the explanatory comment on the line above (matches the file's pervasive "comment-then-key" pattern, lines 32-37, 36-37, 50-51, 60-62).
- Do NOT delete the comment - it documents the field's purpose for future maintainers.
- Do NOT introduce `${ENV_VAR}` interpolation here - the timezone is a hardcoded user constant, not a secret. Compare: secrets like `bot_token: "${DISCORD_BOT_TOKEN}"` (line 15) use interpolation; non-secret literals like `llm_provider: "anthropic"` (line 33) do not.

**Verification pattern** (mirror of Phase 1 Plan 01-04 line 295's `grep` verification of the OpenRouter key substitution):
```bash
# Static check - timezone key is uncommented and set to Asia/Jerusalem
grep -E '^timezone:' config/microclaw.config.yaml
# Expected output: timezone: "Asia/Jerusalem"
```

**No-regression check** (Phase 0 D-17: no hardcoded values in Python):
```bash
# Asia/Jerusalem must NOT appear in Python source - timezone lives in config only
grep -r 'Asia/Jerusalem' src/
# Expected output: (empty - no matches)
```

---

### `Personal-Agent-Hub.lnk` (startup-shortcut) - CREATE OUTSIDE REPO

**Analog:** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Ollama.lnk` on this same machine.

**Why this is the analog:** Same folder, same `.lnk` mechanism, same per-user no-admin install, same `WScript.Shell` creation API. Verified 2026-05-01 in `04-RESEARCH.md` Sources section ("Existing `Ollama.lnk` in user Startup folder - verified via PowerShell `WScript.Shell`, proves `.lnk` mechanism works on this exact machine without admin").

**Properties to set (extracted verbatim from `04-RESEARCH.md` "Pattern 3"):**

| Property | Value | Why |
|----------|-------|-----|
| `TargetPath` | `C:\microclaw\microclaw.exe` | Verified install location (`microclaw --version` returned v0.1.51 from this path) |
| `Arguments` | `start --config "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml"` | Absolute config path; do NOT rely on CWD-based discovery (Open Question 3 in research) |
| `WorkingDirectory` | `C:\Users\galzi\src\personal-agent-hub` | Repo root - same path uv run uses |
| `WindowStyle` | `7` (Minimized) | Avoids the console-window flash that a `.bat` would cause; matches the "clean UX" rationale in research Pattern 3 |
| `Description` | `Personal Agent Hub - MicroClaw runtime auto-start` | For Windows Properties dialog |

**Creation pattern** (PowerShell + WScript.Shell COM, verbatim from `04-RESEARCH.md` "Pattern 3" - the canonical Win32 `.lnk` creation idiom):
```powershell
$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "Personal-Agent-Hub.lnk"

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = "C:\microclaw\microclaw.exe"
$lnk.Arguments        = 'start --config "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml"'
$lnk.WorkingDirectory = "C:\Users\galzi\src\personal-agent-hub"
$lnk.WindowStyle      = 7
$lnk.Description      = "Personal Agent Hub - MicroClaw runtime auto-start"
$lnk.Save()

Write-Output "Created: $lnkPath"
```

**Idempotency** (key property the plan author should preserve): `WScript.Shell.CreateShortcut` opens the existing file if present; `.Save()` overwrites in place. Re-running the snippet is safe and produces no duplicates.

**Critical security pattern** (per `04-RESEARCH.md` Security Domain):
- Use `[Environment]::GetFolderPath("Startup")` (per-user, no admin needed).
- DO NOT use `[Environment]::SpecialFolder::CommonStartup` (all-users; requires admin; fires for every user on the machine; out of scope per D-02).

**Verification pattern** (verbatim from `04-RESEARCH.md` "Pattern 3" verify snippet):
```powershell
$lnkPath = Join-Path ([Environment]::GetFolderPath("Startup")) "Personal-Agent-Hub.lnk"
Test-Path $lnkPath   # expect: True

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
Write-Output "Target:  $($lnk.TargetPath)"
Write-Output "Args:    $($lnk.Arguments)"
Write-Output "WorkDir: $($lnk.WorkingDirectory)"
# Expect:
#   Target  = C:\microclaw\microclaw.exe
#   Args    = start --config "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml"
#   WorkDir = C:\Users\galzi\src\personal-agent-hub
```

---

### `scripts/install-startup-shortcut.ps1` (OPTIONAL utility-script) - NEW, NO IN-REPO ANALOG

**Status:** No project-authored PowerShell or shell script exists in this repository. The `scripts/` directory contains only `git-filter-repo.py` (third-party Python; not a style analog for new PowerShell). The only `.ps1` files anywhere in the working tree are auto-generated `Activate.ps1` files inside `.venv/Scripts/` and `spikes/.venv/Scripts/` - those are uv/Python tooling artifacts, NOT examples of project-authored scripts.

**Recommendation to planner:** This script is OPTIONAL per `04-RESEARCH.md` "Wave 0 Gaps" ("recommended so the snippet is reproducible and auditable, but not required"). Two paths:

1. **Plan task body inlines the PowerShell snippet** (simplest, matches the precedent set by Phase 1 Plan 01-04 which inlines `sqlite3` and Python verification commands directly in `<how-to-verify>` blocks - see lines 137-141 and 192-201 of `01-04-PLAN.md`). Re-running the plan task re-runs the snippet idempotently.
2. **Create `scripts/install-startup-shortcut.ps1`** containing the Pattern 3 PowerShell verbatim. This adds an auditable, version-controlled artifact at the cost of one new file with no in-repo style siblings.

**If path 2 is chosen, the file structure should be:**
```powershell
# scripts/install-startup-shortcut.ps1
# Idempotently creates the Windows user-Startup shortcut for Personal Agent Hub.
# See .planning/phases/04-daily-scheduling/04-RESEARCH.md "Pattern 3" for rationale.
# Re-running this script overwrites the shortcut in place; no duplicates produced.

$ErrorActionPreference = "Stop"

$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "Personal-Agent-Hub.lnk"

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = "C:\microclaw\microclaw.exe"
$lnk.Arguments        = 'start --config "C:\Users\galzi\src\personal-agent-hub\config\microclaw.config.yaml"'
$lnk.WorkingDirectory = "C:\Users\galzi\src\personal-agent-hub"
$lnk.WindowStyle      = 7
$lnk.Description      = "Personal Agent Hub - MicroClaw runtime auto-start"
$lnk.Save()

Write-Output "Created: $lnkPath"
```

**Style notes (since no in-repo analog exists):**
- `$ErrorActionPreference = "Stop"` at the top - PowerShell's equivalent of Python's `set -e`. Standard idiom for scripts intended to fail fast on any cmdlet error.
- Comment header naming the file purpose, the cross-reference to RESEARCH.md, and the idempotency contract. Mirrors the docstring conventions used in the existing Python source (e.g., `src/agent_hub/pipeline.py` opens with a module docstring stating purpose).
- Hard-coded absolute Windows paths. Acceptable here because Phase 0 D-17 ("no hardcoded values") applies to **runtime business logic**, not to one-time install scripts that target this single machine. The MicroClaw exe path and the repo root path are not configurable - they are physical facts of the install.
- No parameters / no parameter block. The script does exactly one thing for one user's machine; parameterizing it would add complexity without benefit for a single-user setup.

---

## Shared Patterns

### Pattern: Idempotent runtime-state mutation with pre-check + write

**Source:** `04-RESEARCH.md` "Pattern 2" (pre-registration cancellation guard) and `04-RESEARCH.md` "Pattern 3" (`.lnk` overwrite-in-place).

**Apply to:**
- The MicroClaw scheduled-task registration prompt sent to the daily-digest channel
- The `.lnk` file creation (in-task or via optional script)

**Idiom:** Before creating new state, query/list existing state and reconcile. After creating, verify by querying the actual stored representation. Both writes must be safe to re-run.

**Code shape:**
```
1. List existing state                    (SQL: SELECT WHERE status='active' AND prompt LIKE '%agent_hub.pipeline%')
2. Cancel duplicates if found             (@-mention: "cancel scheduled task #N")
3. Write new state                        (@-mention: "schedule cron 0 9 * * * ...")
4. Verify write landed                    (SQL: SELECT next_run, schedule_value, timezone)
5. Return write descriptor                (the run_id, the next_run timestamp, the .lnk path)
```

This is the same shape as Phase 1 Plan 01-04 Task 3 (`<how-to-verify>` Steps 1-4: ask, register, inspect DB, verify). The plan author should mirror that step structure for Phase 4 Task 2 (or whichever task registers the schedule).

### Pattern: Verification by sqlite3 query on `microclaw.db`

**Source:** `01-04-PLAN.md` lines 192-201, `04-RESEARCH.md` "Code Examples - SQL Verification Queries".

**Apply to:** Any task that needs to confirm a `scheduled_tasks` row was inserted/cancelled correctly.

**Code excerpt** (Phase 1 precedent, line 239 of `01-04-PLAN.md`):
```bash
sqlite3 "C:\Users\galzi\.microclaw\runtime\microclaw.db" "SELECT id, schedule_type, schedule_value, next_run, status FROM scheduled_tasks ORDER BY created_at DESC LIMIT 3;"
```

**Phase 4 specialization** (from `04-RESEARCH.md` "Code Examples - Post-registration verification"):
```sql
SELECT id, schedule_type, schedule_value, timezone, status, next_run, prompt
FROM scheduled_tasks
WHERE status = 'active'
  AND prompt LIKE '%agent_hub.pipeline%';
-- Expected: exactly 1 row
--   schedule_type  = 'cron'
--   schedule_value = '0 9 * * *'   (or 6-field equivalent '0 0 9 * * *')
--   timezone       = 'Asia/Jerusalem' or '' (empty - global config used)
--   status         = 'active'
--   next_run       = future ISO timestamp <= 24h from now
```

### Pattern: @-mention as the only inbound channel to MicroClaw

**Source:** `00-validation-spikes/00-01-PLAN.md` interface F1, restated in `01-04-PLAN.md` line 73.

**Apply to:** Any task that needs the agent to take an action (cancel, schedule, post). The plan must NEVER instruct a plain channel message - those are silently dropped.

**Code excerpt** (verbatim from `01-04-PLAN.md` line 73):
```
F1: @-mention is REQUIRED for inbound flows. Plain-text channel messages are silently dropped.
    Format: "@Personal Agent Hub <prompt>"
    Channel: use the daily-digest channel (create if it does not exist)
```

**Phase 4 specialization:** The two prompts the plan author will send are captured verbatim in `04-RESEARCH.md` "Pattern 1" (registration) and "Pattern 2" (pre-registration cancellation guard). Use those strings without modification.

### Pattern: No hardcoded timezone in Python (Phase 0 D-17)

**Source:** Phase 0 D-17 cited in `04-CONTEXT.md` "Established Patterns".

**Apply to:** Any Python file the planner might be tempted to touch. Phase 4 should NOT modify any `.py` file. If it does, this pattern is violated.

**Negative test pattern** (the planner should add this exact check to verification):
```bash
grep -r 'Asia/Jerusalem' src/
# Expected: (empty)
```

If a future phase needs Python-side timezone arithmetic, `tzdata` must be added to dependencies (`uv add tzdata`); see `04-RESEARCH.md` "Pitfall 5".

---

## No Analog Found

Files / artifacts with no close match in this codebase. The planner should use `04-RESEARCH.md` patterns directly:

| Artifact | Role | Data Flow | Reason | Substitute Source |
|----------|------|-----------|--------|-------------------|
| `Personal-Agent-Hub.lnk` (Windows binary shortcut) | startup-shortcut | OS-event | No `.lnk` exists in this repo (and nor should one - it must live in `%APPDATA%\…\Startup\` per D-02). The same-machine `Ollama.lnk` is the OS-precedent but is not a code analog. | `04-RESEARCH.md` "Pattern 3" provides the verbatim PowerShell creation snippet and verification snippet. |
| `scripts/install-startup-shortcut.ps1` | utility-script | one-shot | No project-authored PowerShell or shell scripts exist in the repo. `scripts/` contains only `git-filter-repo.py`, which is third-party Python and not a style analog. | `04-RESEARCH.md` "Pattern 3" + the inline structure suggested in Pattern Assignments above. Style decisions (`$ErrorActionPreference = "Stop"`, no parameters, comment header) are first-time-in-repo conventions. |
| `scheduled_tasks` row | runtime-state | DB-row | This is not a file at all. It is a SQLite row inserted at runtime by the MicroClaw agent in response to an `@-mention`. | `04-RESEARCH.md` "Pattern 1" provides the verbatim registration prompt. |

---

## Metadata

**Analog search scope:**
- `config/` - found the target file for the timezone edit
- `scripts/` - confirmed no project-authored scripts (only third-party `git-filter-repo.py`)
- Whole repo for `*.ps1`, `*.bat`, `*.sh` - all matches are venv-generated, none are project-authored
- `.planning/phases/01-ingestion-foundation/` - mined Plan 01-04 for the schedule-registration precedent and `sqlite3` verification idiom
- `.planning/phases/04-daily-scheduling/04-RESEARCH.md` - the canonical source for Patterns 1-4 used by Phase 4

**Files scanned:** 8
- `config/microclaw.config.yaml` (target file - read in full)
- `scripts/git-filter-repo.py` (confirmed third-party, not a style analog)
- `.planning/phases/01-ingestion-foundation/01-04-PLAN.md` (precedent for schedule registration + sqlite3 verification)
- `.planning/phases/01-ingestion-foundation/01-PATTERNS.md` (precedent for PATTERNS.md format)
- `.planning/phases/03-source-coverage-fix/03-PATTERNS.md` (most-recent PATTERNS.md format)
- `.planning/phases/04-daily-scheduling/04-CONTEXT.md` (decisions D-01 through D-05)
- `.planning/phases/04-daily-scheduling/04-RESEARCH.md` (Patterns 1-4, verbatim PowerShell, verbatim prompts)
- `.planning/phases/00-validation-spikes/00-01-PLAN.md` (interface F1: @-mention contract)

**Pattern extraction date:** 2026-05-01

**Key constraint for the planner:** Phase 4 has zero new code files in the project tree (the optional `.ps1` is at the planner's discretion). The phase is dominated by (1) one YAML one-liner edit, (2) one out-of-repo `.lnk` creation, and (3) one runtime SQL row inserted via natural-language `@-mention`. The planner should NOT invent file changes that the research and context do not call for.
