# Phase 2: Thin Digest - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-26
**Phase:** 2-thin-digest
**Areas discussed:** Item format, Message structure, Long list handling, Which items to list, URL embed suppression, Digest intro line, Pipeline return type, run_digest() return type change, MicroClaw multi-post wiring, Dedup scope, Discord channel ID storage, run_digest() backward compat, Discord API posting pattern, Test strategy for direct Discord posting, Error handling for Discord API failures, MicroClaw scheduled task prompt update

---

## Item Format

| Option | Description | Selected |
|--------|-------------|----------|
| Title + Source | `• Title [Source]` - clean, no URL | |
| Title + Source + URL | Title + source on line 1, URL on line 2 | ✓ |

**User's choice:** Title + Source + URL

| Option | Description | Selected |
|--------|-------------|----------|
| Truncate at ~80 chars | Keeps list consistent | ✓ |
| Show full title | Full context preserved | |

**User's choice:** Truncate at ~80 chars

| Option | Description | Selected |
|--------|-------------|----------|
| Bullet points • | Order doesn't imply ranking | ✓ |
| Numbered 1. 2. 3. | Easier to reference | |

**User's choice:** Bullet points •

| Option | Description | Selected |
|--------|-------------|----------|
| Chronological / as-ingested | Simple, no grouping logic | ✓ |
| Grouped by source | Clusters sources together | |

**User's choice:** Chronological / as-ingested

---

## Message Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Combined - status header + items below | One Discord message | ✓ |
| Two messages - status first, then item list | Status posts immediately, then second message | |

**User's choice:** Combined - status header + items below

| Option | Description | Selected |
|--------|-------------|----------|
| Keep no-items message as-is | Phase 1 ⚠️ message is fine | ✓ |
| Add brief explanation | Explain why nothing passed filter | |

**User's choice:** Keep as-is

---

## Long List Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Cap at N items, add '...and N more' | Single message always | |
| Split into multiple messages | Post all items across messages | ✓ |

**User's choice:** Split into multiple messages

| Option | Description | Selected |
|--------|-------------|----------|
| Fill to ~1800 chars per message | Pack as many as fit | ✓ |
| Fixed cap of 10 items per message | Predictable batches | |

**User's choice:** Fill to ~1800 chars per message

---

## Which Items to List

| Option | Description | Selected |
|--------|-------------|----------|
| Relevant items only (post-filter) | Items that passed AI relevance filter | ✓ |
| All fetched items (pre-filter) | Everything RSS feeds returned | |

**User's choice:** Relevant items only (post-filter)

| Option | Description | Selected |
|--------|-------------|----------|
| Current run only | Simple, in-scope | ✓ |
| Include missed items from prior failures | Catch-up logic | |

**User's choice:** Current run only

---

## URL Embed Suppression

| Option | Description | Selected |
|--------|-------------|----------|
| Suppress previews with <URL> | Angle brackets block embed card | ✓ |
| Bare URL - allow previews | Full Discord embed cards per item | |

**User's choice:** Suppress previews with `<URL>` - keeps digest scannable with many items

---

## Digest Intro Line

| Option | Description | Selected |
|--------|-------------|----------|
| Yes - '📰 Today's AI updates:' | Visual break between status and content | ✓ |
| No header - items start directly | More compact | |

**User's choice:** Yes - "📰 Today's AI updates:" header

---

## Pipeline Return Type

| Option | Description | Selected |
|--------|-------------|----------|
| Return list[str] from run_digest() | MicroClaw posts each list item | |
| New format_digest() helper returns list[str] | run_digest() wraps and handles posting | ✓ |
| Keep str, handle in MicroClaw config | Check MicroClaw native multi-post support | |

**User's choice:** New `format_digest()` helper returns `list[str]`

---

## MicroClaw Multi-Post Wiring

| Option | Description | Selected |
|--------|-------------|----------|
| Pipeline posts to Discord directly via HTTP | Pipeline = poster, MicroClaw = scheduler | ✓ |
| Return sentinel-delimited string to MicroClaw | LLM splits on sentinel and posts each part | |
| Planner decides - check MicroClaw capability | Let researcher verify native support first | |

**User's choice:** Pipeline posts to Discord directly via HTTP (Discord REST API)

| Option | Description | Selected |
|--------|-------------|----------|
| Pipeline posts everything, MicroClaw gets silent confirmation | No double-post | ✓ |
| MicroClaw posts status, pipeline posts items separately | Two separate actors | |

**User's choice:** Pipeline posts everything, MicroClaw gets silent confirmation

---

## Discord Channel ID Storage

| Option | Description | Selected |
|--------|-------------|----------|
| Add DISCORD_CHANNEL_ID to .env | Consistent with other secrets | ✓ |
| Add to config/microclaw.config.yaml | Groups Discord config together | |
| New config/discord.yaml | Dedicated Discord config file | |

**User's choice:** `DISCORD_CHANNEL_ID` in `.env`

---

## run_digest() Backward Compat

| Option | Description | Selected |
|--------|-------------|----------|
| No - update tests to match new behavior | Clean contract | ✓ |
| Yes - keep str return, add post_digest() | Two entry points | |

**User's choice:** Update tests to new behavior - no backward compat wrapper

---

## Discord API Posting Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Bot token + channel ID via Discord REST API | Direct HTTP, no extra deps | ✓ |
| Webhook URL | Simpler auth but requires webhook setup | |

**User's choice:** Discord REST API v10

---

## Test Strategy for Direct Discord Posting

| Option | Description | Selected |
|--------|-------------|----------|
| Mock httpx calls to Discord API | No real network, consistent pattern | ✓ |
| Inject posting callable | run_digest(poster=...) accepts callable | |
| Skip Discord posting via env var | DISCORD_SKIP_POST=1 | |

**User's choice:** Mock httpx calls with respx or httpx mock transport

---

## Error Handling for Discord API Failures

| Option | Description | Selected |
|--------|-------------|----------|
| Log error, mark run as 'partial', continue | New partial status, no retry | ✓ |
| Retry failed chunk once, then log | More resilient | |
| All-or-nothing - if any chunk fails, run fails | Strict consistency | |

**User's choice:** Log error, mark run as `partial`, continue

---

## MicroClaw Scheduled Task Prompt Update

| Option | Description | Selected |
|--------|-------------|----------|
| Yes - update prompt to 'run pipeline, it will post itself' | Prevents double-posting | ✓ |
| No - test first to see if MicroClaw double-posts | Let planner verify first | |

**User's choice:** Yes - update prompt

---

## Claude's Discretion

- Whether `format_digest()` lives in `discord.py` or a new `formatter.py` module
- Exact `respx` vs `httpx` mock transport choice for tests
- Whether `config.py` gets a `load_discord_config()` helper or env vars read inline
- Discord API rate limit handling (likely a non-issue for Phase 2 volumes)

## Deferred Ideas

- Deduplication across sources - Phase 3 (Canonical Story Formation)
- Per-source machine-actionable filter rules - Phase 4/5
- Retry logic for Discord API failures - later phase
- Discord rate limit handling - later phase (volumes too low in Phase 2 to matter)
- `rejected_items` table - noted again from Phase 1 deferred, still deferred
