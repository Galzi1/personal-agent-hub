# Phase 2: Thin Digest - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Post a formatted list of relevant ingested items to Discord daily, giving the user a tangible digest artifact before dedup and ranking exist. This phase validates the end-to-end pipeline (schedule → ingest → format → deliver) and shifts the pipeline from status-only notifications to actual content delivery.

**In scope:**
- A `format_digest()` function that formats relevant items and splits content into Discord-safe chunks (list[str])
- Direct Discord REST API posting from the pipeline (not via MicroClaw stdout)
- A "📰 Today's AI updates:" intro line before item list
- Status header combined with item list in the first message
- `runs` table extended with a `partial` status for mid-stream Discord API failures

**Out of scope:**
- Deduplication of items appearing across multiple sources (Phase 3)
- Ranking or topic-based sections (Phase 4)
- Feedback or mute controls (Phase 5)
- Inbound flows / user commands

</domain>

<decisions>
## Implementation Decisions

### Item Format
- **D-01:** Each item formatted as two lines: `• [Title] [Source]` on line 1, `  <URL>` on line 2. Angle brackets suppress Discord link preview embeds.
- **D-02:** Titles truncated at ~80 characters to keep list scannable.
- **D-03:** Bullet points (`•`), not numbered list - order does not imply ranking (that comes in Phase 4).
- **D-04:** Chronological / as-ingested order. No grouping by source - Phase 4 adds topic sections.
- **D-05:** No deduplication - if the same story appears from two sources, it appears twice. Phase 3 handles canonical story formation.

### Message Structure
- **D-06:** Combined message: status header (existing Phase 1 format) + blank line + `📰 Today's AI updates:` intro line + item list, all in the first Discord message.
- **D-07:** When no relevant items: existing Phase 1 `⚠️ Run #N ...` message unchanged - no item list sent.
- **D-08:** When run fails: existing Phase 1 `❌ Run #N failed` message unchanged.

### Long List Handling
- **D-09:** When combined message would exceed ~1800 chars, split into multiple Discord messages. Fill each message to ~1800 chars before starting the next. No hard cap on number of messages.
- **D-10:** `format_digest(items, run_num, dt, run_id, raw_count, source_count) -> list[str]` is the new formatting entry point. Returns a list of Discord-ready message strings. The first string contains the status header + intro + initial items; subsequent strings contain overflow items only.

### Discord Posting - Architecture Shift
- **D-11:** Pipeline posts to Discord directly via Discord REST API. MicroClaw is no longer responsible for posting content messages - it only triggers the run.
- **D-12:** Posting mechanism: `POST https://discord.com/api/v10/channels/{channel_id}/messages` with `Authorization: Bot {token}` header and `{"content": "..."}` body. Uses existing `httpx` client (already a dependency).
- **D-13:** `DISCORD_CHANNEL_ID` added to `.env` alongside existing `DISCORD_BOT_TOKEN`. Pipeline reads both from environment.
- **D-14:** MicroClaw scheduled task prompt updated to reflect self-posting pipeline. New prompt should say the pipeline posts its own output to Discord - prevents MicroClaw from also posting the return value (double-post).
- **D-15:** `run_digest()` return value changes from the formatted Discord message string to a minimal confirmation string (e.g., `"posted N messages"` or `"done"`). MicroClaw receives this confirmation but does not post it.

### Error Handling
- **D-16:** If Discord API call fails mid-stream (e.g., 2 of 3 chunks posted): log the error, mark the run status as `partial` in the `runs` table, and continue without retry. User receives partial content rather than nothing. Phase 2 does not implement retry logic.
- **D-17:** `runs` table needs a new `partial` status value alongside existing `success`, `failure`, `no_items`.

### Testing
- **D-18:** Discord API HTTP calls in tests are mocked via `respx` (or `httpx`'s built-in mock transport). No real network calls in tests. Consistent with existing test patterns that mock OpenRouter calls.
- **D-19:** Phase 1 tests that assert `run_digest()` returns a specific formatted string are updated - they now assert the correct Discord API calls were made and that `run_digest()` returns a confirmation string.

### Claude's Discretion
- Whether `format_digest()` lives in `discord.py` (extending existing format helpers) or a new `formatter.py` module
- Exact `respx` vs `httpx` mock transport choice for test implementation
- Whether `config.py` gets a `load_discord_config()` helper or environment vars are read inline in `discord.py`
- How Discord API rate limits (5 messages/5 sec per channel) are handled if ever hit - basic `time.sleep()` or ignored in Phase 2

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Prior Phase Decisions (locked)
- `.planning/phases/01-ingestion-foundation/01-CONTEXT.md` - Phase 1 locked decisions. Critical: D-08 (status message formats), D-12 (raw_items schema), D-14 (runs table schema), D-15 (08:00 schedule), D-13 (only relevant items stored).
- `.planning/phases/00-validation-spikes/00-CONTEXT.md` - Phase 0 locked decisions. Critical: D-13/D-14 (OpenRouter sole LLM provider), D-15 (per-task model selection), D-17 (no hardcoded model IDs), D-19/D-20 (config layout), D-23/D-24 (outbound-only, @-mention contract).
- `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md` - MicroClaw contracts (F1: @-mention required for inbound, F2-F4).

### Project Requirements
- `.planning/PROJECT.md` - Core constraints: Windows-first, Discord delivery, single-user, planning guard.
- `.planning/REQUIREMENTS.md` - Active requirements list.

### Existing Config
- `config/microclaw.config.yaml` - MicroClaw runtime config (gitignored). Discord bot_token reference.
- `config/sources.yaml` - 7 active RSS feeds. Phase 2 does not modify this.
- `config/models.yaml` - Per-task model assignments. Phase 2 does not add new task types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/agent_hub/discord.py` - Contains `format_success()`, `format_failure()`, `format_no_items()`. Phase 2 adds `format_digest()` to this module (or a new formatter module per Claude's discretion).
- `src/agent_hub/pipeline.py` - `run_digest()` orchestrates ingest → filter → DB → notify. Phase 2 modifies the Step 6 (Notify) section to call Discord API directly instead of returning the message string.
- `src/agent_hub/db.py` - `runs` table CRUD. Phase 2 adds `partial` as a valid status value.
- `src/agent_hub/config.py` - Config loading helpers. Phase 2 may add `load_discord_config()` for bot token + channel ID.

### Established Patterns
- **httpx client** already used in `ingester.py` and `filter.py` for HTTP calls. Discord API posting reuses the same pattern.
- **Environment-based secrets** (`.env`): `DISCORD_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`. `DISCORD_CHANNEL_ID` follows the same pattern.
- **Test mocking**: existing tests mock OpenRouter HTTP responses. Discord API mocking follows the same pattern with `respx` or `httpx` mock transport.
- **No hardcoded values** (D-17 from Phase 0): model IDs in `models.yaml`, tokens in env vars, channel IDs in env vars.

### Integration Points
- `pipeline.py` → `discord.py`: currently `run_digest()` calls `format_*()` and returns the string. Phase 2: calls `format_digest()` → gets `list[str]` → posts each via Discord REST API → returns confirmation.
- `.env` → `pipeline.py`: `DISCORD_CHANNEL_ID` and `DISCORD_BOT_TOKEN` read from environment.
- MicroClaw scheduled task → `uv run python -m agent_hub.pipeline`: MicroClaw prompt updated to reflect self-posting behavior.
- `runs` table: `partial` status added for mid-stream Discord API failures.

### Phase 1 Confirmed Output (Live Run)
- Run #11: 1132 fetched → 12 relevant items. Shows typical item counts. 12 items × ~120 chars each (title+source+URL) ≈ 1440 chars - likely fits in one message, but splitting logic needed for high-volume days.

</code_context>

<specifics>
## Specific Ideas

**Confirmed message format (user-approved preview):**
```
✅ Run #4 - 2026-04-26 08:00
12 fetched → 5 relevant items from 7 sources

📰 Today's AI updates:
• GPT-5 quietly announced [OpenAI Blog]
  <https://openai.com/blog/gpt5>
• Cursor adds agent mode [The Verge]
  <https://theverge.com/2026/...>
```

**Multi-message split (when overflow):**
- Message 1: Status header + intro + items 1-N (up to ~1800 chars)
- Message 2: Items N+1-M (continuation, up to ~1800 chars)
- No "continued..." header needed on overflow messages - Discord timestamps make sequence clear

**Discord REST API call:**
```
POST https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages
Authorization: Bot {DISCORD_BOT_TOKEN}
Content-Type: application/json
{"content": "..."}
```

**Partial status in runs table:**
- New `partial` status: Discord API posted some but not all message chunks
- `error_message` field records which chunk failed and the HTTP error

</specifics>

<deferred>
## Deferred Ideas

- **Deduplication across sources** - same story appearing on OpenAI Blog AND The Verge is shown twice in Phase 2. Phase 3 (Canonical Story Formation) collapses duplicates.
- **Per-source filtering hints** - `sources.yaml` has human-readable `note` fields (e.g., "High RC/patch noise"). Machine-actionable filter rules deferred from Phase 1; still deferred to Phase 4/5.
- **Retry logic for Discord API failures** - Phase 2 logs and marks partial. Retry strategy deferred.
- **Discord rate limit handling** - If many messages posted rapidly, Discord enforces 5 msg/5s per channel. Phase 2 ignores this (12 items = 1-2 messages, well within limits). Explicit rate limiting deferred.
- **`rejected_items` table** - items that fail relevance filter are not stored. Noted as potentially useful for debugging in Phase 1 deferred. Still deferred to a later phase.

</deferred>

---

*Phase: 2-Thin-Digest*
*Context gathered: 2026-04-26*
