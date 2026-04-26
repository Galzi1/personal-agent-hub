# Phase 1: Ingestion Foundation & Run Visibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-25
**Phase:** 01-ingestion-foundation
**Areas discussed:** Source config format, Run status Discord UX, Raw item data schema, OpenRouter in Phase 1

---

## Source Config Format

| Option | Description | Selected |
|--------|-------------|----------|
| config/sources.yaml | Dedicated YAML file alongside models.yaml. User-editable, consistent with D-19. Phase 4 mute-a-source writes here. | ✓ |
| Inline in agent template | URLs in MicroClaw prompt/template. Simpler now, harder to maintain. | |
| Python constants file | src/config/sources.py. Requires code change to edit. | |

**User's choice:** config/sources.yaml

---

## Source Config - Per-source Filtering Notes

| Option | Description | Selected |
|--------|-------------|----------|
| Raw only in Phase 1 | Ingest everything, no filter hints. Phase 2 handles noise. | |
| Add filter hints to sources.yaml | Optional `note` field per source. Phase 1 doesn't act on them. | ✓ |

**User's choice:** Add filter hints - `note` field as human-readable metadata. Phase 1 does not execute on notes.

---

## Run Status Discord UX - Success Format

| Option | Description | Selected |
|--------|-------------|----------|
| Single status line | `✅ Run #N - date\nX items from Y sources` | ✓ |
| Per-source breakdown | Success line + per-source table (7 lines per run) | |
| Silent on success | No message on clean success - only failures/no-items | |

**User's choice:** Single status line

---

## Run Status Discord UX - Failure & No-Items Format

| Option | Description | Selected |
|--------|-------------|----------|
| Separate message per case | Distinct format + details for failure vs no-items | ✓ |
| Same format, different emoji | Single-line format with emoji swap only | |

**User's choice:** Separate message per case with error reason on failure

---

## Raw Item Data Schema

| Option | Description | Selected |
|--------|-------------|----------|
| Title + link + source + date + summary | 8 fields. RSS summary included for Phase 1.5 display and Phase 2 dedup. | ✓ |
| Title + link + source + date only | 7 fields. Phase 2 must re-fetch for dedup. | |
| Full content capture | Everything feedparser returns. Unknown size, messier schema. | |

**User's choice:** title + link + source + date + summary (8 fields)

---

## OpenRouter Role in Phase 1

| Option | Description | Selected |
|--------|-------------|----------|
| Smoke test only | One verification call, not in daily run hot path. All items stored raw. | |
| Light relevance pre-filter | OpenRouter in hot path every run. Discards non-AI-relevant items. | ✓ |

**User's choice:** Light relevance pre-filter in hot path

---

## Relevance Filter Criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Keep: AI-relevant only | Models, AI coding tools, new AI tools, notable updates, hot trends. Discard tutorials, non-AI releases. | ✓ |
| Keep: anything new/release-like | Broader - anything that announces something new. | |

**User's choice:** AI-relevant only

---

## Relevance Filter Model

| Option | Description | Selected |
|--------|-------------|----------|
| Same as ranking model | Reuse D-18 ranking model (Gemini Flash Preview). One model, two tasks. | ✓ |
| Dedicated cheap fast model | Separate `relevance` task type with cheapest available model. | |

**User's choice:** Same as ranking model - new `relevance` task type in models.yaml pointing to same model as `ranking`

---

## Run Status - Raw vs Filtered Count

| Option | Description | Selected |
|--------|-------------|----------|
| Show both counts | `18 fetched → 12 relevant items` - transparent about filtering | ✓ |
| Relevant items only | Show only post-filter count | |

**User's choice:** Show both counts

---

## Claude's Discretion

- SQLite migration approach
- Retry/timeout defaults for httpx feed fetches
- Relevance filter prompt design (few-shot vs zero-shot)
- Batch vs per-item OpenRouter calls for relevance filter
- Test fixture strategy

## Deferred Ideas

- Machine-actionable per-source filter rules → Phase 2
- `rejected_items` table → may be added in Phase 2 for filter quality debugging
- Control panel model-selection UI → tracked from Phase 0 deferred
- DM-based bot-receiver flow → Phase 2+ (D-23/D-24)
