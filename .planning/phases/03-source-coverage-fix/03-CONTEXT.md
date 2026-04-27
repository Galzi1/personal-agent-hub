# Phase 3: Source Coverage Fix - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Diagnose and fix why the first live run produced items exclusively from OpenAI Blog. Ensure ≥3 distinct sources appear in each digest when available. Add per-source item count visibility to detect coverage regressions.

**In scope:**
- A 48-hour recency window applied before the LLM relevance filter (drops stale items)
- Raise total filter cap from 50 → 150 items (safety cap after recency window)
- Per-source item counts logged via `logger.info` and surfaced in Discord success message
- Discord `⚠️` warning when post-filter results come from <3 distinct sources
- `source_count` in success message changed from enabled-sources count to contributing-sources count

**Out of scope:**
- Deduplication across sources (Phase 6)
- Ranking or topic-based sections (Phase 10)
- Per-source mute/filter rules (future phase)
- Retry logic for Discord API failures (deferred from Phase 2)

</domain>

<decisions>
## Implementation Decisions

### Recency Window (root cause fix)

- **D-01:** Apply a 48-hour recency window in `filter.py` before pooling items for the LLM filter. Items with `published_at` older than `now - 48h` are excluded. Items with `published_at = None` (missing date) are included (conservative - don't silently drop them).
- **D-02:** Raise the total safety cap from 50 → 150 items after the recency window is applied. The recency window naturally limits volume; the cap is a backstop for burst days (e.g., major model launch with 200+ posts).
- **D-03:** Sources with 0 items surviving the recency window: skip silently with `logger.warning(f"{source_name}: 0 items in 48h window - skipped")`. No forced inclusions. Coverage goal is ≥3 sources, not all 7.

### Per-Source Count Visibility

- **D-04:** Log per-source item counts at two pipeline stages via `logger.info`:
  1. After ingestion: `"{source_name}: {n} items fetched"`
  2. After relevance filter: `"{source_name}: {n} items passed filter"`
- **D-05:** Update the Discord SUCCESS message to include a per-source breakdown line. Format:
  ```
  ✅ Run #N - YYYY-MM-DD HH:MM
  {raw} fetched → {relevant} relevant from {contributing_source_count} sources
  (OpenAI Blog: 3, TestingCatalog: 3, Simon Willison: 2, Latent Space: 1)
  Run ID: run-N-YYYY-MM-DD
  ```
- **D-06:** `source_count` in the status line changes meaning: it now counts contributing sources (those with ≥1 item after filter), not enabled/configured sources. `format_digest()` signature and callers must be updated accordingly.
- **D-07:** No-items and failure messages remain unchanged per Phase 1 D-08. The per-source breakdown appears only on success runs.

### Coverage Enforcement

- **D-08:** Threshold: 3 distinct contributing sources (per ROADMAP Phase 3 SC2).
- **D-09:** When post-filter results come from <3 sources, add a Discord warning to the success message:
  ```
  ✅ Run #N - YYYY-MM-DD HH:MM
  11 fetched → 4 relevant from 2 sources ⚠️
  (OpenAI Blog: 3, Latent Space: 1)
  ⚠️ Only 2 sources represented - check filters
  Run ID: run-N-YYYY-MM-DD
  ```
  The `⚠️` appended to the source count line is the inline signal; the separate warning line is the actionable message.
- **D-10:** No forced inclusions - do not override the relevance filter to hit the 3-source threshold. Log the coverage miss and warn the user; fixing it requires a config or filter change, not an automatic override.

### Testing

- **D-11:** Tests must cover: (a) recency window excludes old items, (b) missing `published_at` items pass through, (c) per-source breakdown format in Discord message, (d) `⚠️` warning triggered when <3 sources pass filter. Existing mock patterns (`respx` for OpenRouter and Discord API) apply.

### Claude's Discretion

- Where in `filter.py` or `pipeline.py` the recency window logic lives (inline in pipeline vs. helper in ingester/filter)
- Exact datetime comparison approach (UTC-aware vs. naive, `timedelta(hours=48)` vs. `timedelta(days=2)`)
- Whether `format_digest()` receives a `source_breakdown: dict[str, int]` param or derives it from `items`
- How the breakdown line handles sources with very long names (truncation threshold)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Prior Phase Decisions (locked)

- `.planning/phases/02-thin-digest/02-CONTEXT.md` - Phase 2 locked decisions. Critical: D-10 (`format_digest()` signature with `source_count`), D-11 (direct Discord REST API posting), D-12 (Discord API call format), D-15 (return value is confirmation string, not message content).
- `.planning/phases/01-ingestion-foundation/01-CONTEXT.md` - Phase 1 locked decisions. Critical: D-08 (Discord message formats for all three run outcomes - must not break), D-12 (`raw_items` schema including `source_name` field), D-14 (`runs` table schema).
- `.planning/phases/00-validation-spikes/00-CONTEXT.md` - Phase 0 locked decisions. Critical: D-13/D-14 (OpenRouter sole LLM provider), D-17 (no hardcoded model IDs), D-19/D-20 (config layout).

### Project Requirements

- `.planning/PROJECT.md` - Core constraints: Windows-first, Discord delivery, planning guard.
- `.planning/REQUIREMENTS.md` - Active requirements list.

### Existing Source Files (read before planning)

- `src/agent_hub/filter.py` - Contains 50-item cap (`items[:50]`) to fix and relevance filter logic.
- `src/agent_hub/pipeline.py` - Orchestrates ingest → filter flow; `source_count` variable to update.
- `src/agent_hub/discord.py` - `format_digest()` to extend with per-source breakdown.
- `config/sources.yaml` - 7 feeds, 2 disabled. Source order matters for current cap bug diagnosis.

</canonical_refs>

<code_context>
## Existing Code Insights

### Root Cause (confirmed via code reading)

- `filter.py:44` - `items[:50]` truncates the combined pool. `sources.yaml` lists OpenAI Blog first. If OpenAI Blog returns 30 items, only 20 slots remain for 6 other sources. This is the primary source starvation cause.
- `pipeline.py:44-45` - `source_count` counts enabled sources (configured), not contributing sources. The status message claims "from 7 sources" even when only 1 contributed.

### Reusable Assets

- `src/agent_hub/ingester.py` - `RawItem.published_at` is already an ISO datetime string (or None). Recency check reads this field directly.
- `src/agent_hub/discord.py` - `format_digest()` already receives `source_count`; Phase 3 changes this param's meaning and adds `source_breakdown`.
- `src/agent_hub/db.py` - `raw_items` table already stores `source_name` per item; breakdown counts can be derived from in-memory `relevant_items` without DB query.

### Established Patterns

- **Date handling**: `published_at` stored as UTC ISO string (from `datetime(*parsed_date[:6], tzinfo=timezone.utc).isoformat()` in ingester). Parse back to `datetime` for comparison.
- **httpx for HTTP**: all HTTP calls use httpx. No new HTTP client needed.
- **Test mocking**: OpenRouter and Discord API calls mocked via `respx`. Apply same pattern to any new network-touching code.
- **No hardcoded values** (Phase 0 D-17): the 48h window and 150-item cap should be constants (not magic numbers inline), or eventually configurable in `config/sources.yaml` or a new key.

### Integration Points

- `pipeline.py` → `filter.py`: recency window applied before `relevance_filter()` call (or inside it - Claude's discretion).
- `pipeline.py` → `discord.py`: `format_digest()` call updated to pass contributing-source breakdown instead of total source count.
- Tests: existing tests that assert on `format_digest()` output must be updated for new message format.

</code_context>

<specifics>
## Specific Ideas

**Confirmed Discord success message format (user-approved preview):**
```
✅ Run #5 - 2026-04-28 09:00
18 fetched → 9 relevant from 4 sources
(OpenAI Blog: 3, TestingCatalog: 3, Simon Willison: 2, Latent Space: 1)
Run ID: run-5-2026-04-28
```

**Coverage warning format (user-approved preview):**
```
✅ Run #5 - 2026-04-28 09:00
11 fetched → 4 relevant from 2 sources ⚠️
(OpenAI Blog: 3, Latent Space: 1)
⚠️ Only 2 sources represented - check filters
Run ID: run-5-2026-04-28
```

**Sources with 0 items in 48h window:**
`logger.warning(f"{source_name}: 0 items in 48h window - skipped")`
No Discord alert for this - only the per-source breakdown reveals it implicitly.

</specifics>

<deferred>
## Deferred Ideas

- **Per-source filtering rules** (machine-actionable, beyond human notes in sources.yaml) - deferred from Phase 1, still deferred. Phase 3 fixes coverage via recency window; source-specific filter rules belong in a later phase.
- **SQLite `source_stats` table** for queryable per-source history - useful later but not required for Phase 3's regression-visibility goal. Discord breakdown + logger covers it.
- **Configurable recency window per source** - some sources post infrequently (DeepMind ~2/week); a per-source window (e.g., 72h for DeepMind) was considered but deferred. Global 48h window is sufficient for Phase 3.

</deferred>

---

*Phase: 3-Source-Coverage-Fix*
*Context gathered: 2026-04-27*
