# Personal Agent Hub

## What This Is

Personal Agent Hub is a personal AI-agent system for non-coding personal and business work. It is meant to monitor AI developments, surface useful resources, generate post ideas, and support future research workflows; v1 starts with a Discord-delivered daily AI news feed that filters the highest-signal updates about new models, notable product changes in tools like Claude Code and Cursor, interesting new AI tools, and hot trends.

## Core Value

Deliver a high-signal, low-noise AI intelligence feed early enough to be useful, instead of making the user hunt through repetitive posts after everyone else has already amplified them.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Deliver a daily AI news digest to Discord for a single user.
- [ ] Prioritize relevance over volume by filtering low-signal items and collapsing duplicate coverage of the same update.
- [ ] Cover new model releases, important updates in AI coding tools, interesting new AI tools, and hot trends.
- [ ] Keep major agent handoffs and completions visible in chat and traceable in the control panel.
- [ ] Build on a local-first agent foundation that can later expand into resource discovery, post-idea generation, and competitor, prospect, or partner research.

### Out of Scope

- Multi-user collaboration in v1 — the first release is only for the project owner.
- A full worker mesh across every planned workflow — prove one visible end-to-end workflow before expanding.
- Software-development automation as the primary product goal — the system is for personal and business intelligence work, not coding workflows.
- Broad multi-channel delivery at launch — Discord is the first delivery surface; other channels can follow later.
- Full competitor, prospect, and partner research automation in v1 — valuable later, but not part of the first proof point.

## Context

- The current workflow is manual: tracking AI news through LinkedIn, Chrome's new-tab feed, and WhatsApp communities.
- The main pain is noise: the same update appears repeatedly across sources, and discovery is reactive enough that the user often hears about items after many other people have already posted about them.
- Existing architecture notes point toward MicroClaw as the system foundation, with Ollama, shared storage, observability, and a control panel on Windows.
- The current design direction favors visible routing: major handoffs and completions should appear in chat, while the control panel remains the forensic layer for traces and low-level state.
- The current memory direction is layered memory: agent-local durable memory plus a smaller shared project memory, with explicit promotion of validated wins.
- The initial product slice should prove one visible workflow, then grow into adjacent personal and business workflows such as resource discovery, post ideas, and market research.

## Constraints

- **Platform**: Windows-first foundation around MicroClaw and Ollama — existing architecture work already assumes this stack.
- **Delivery**: Discord-first for v1 — the digest must arrive where the user already wants to consume it.
- **Audience**: Single-user initial release — no v1 need for shared roles, permissions, or client-facing behavior.
- **Signal Quality**: Relevance and deduplication matter more than raw coverage — reducing noise is a success condition, not a nice-to-have.
- **Architecture**: Major handoffs must stay visible in chat and auditable in the control panel — trust and debugging depend on this.
- **Scope**: Prove one end-to-end workflow before expanding worker taxonomy or channel coverage — avoid overbuilding the full architecture upfront.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use MicroClaw as the system foundation | It matches the current architecture direction with native Ollama support, Windows support, a control plane, and first-class sub-agents | — Pending |
| Start with a Discord-delivered daily AI news feed | One visible, high-value workflow is a better first proof point than building the full worker mesh | — Pending |
| Optimize for high-signal relevance over maximum coverage | The user's biggest pain is noisy duplicate reporting and reactive discovery | — Pending |
| Treat the product as a personal and business task hub, not a coding agent | The intended value is AI intelligence, resource discovery, idea generation, and research support | — Pending |
| Use layered memory with agent-local and shared project memory | Durable context should be curated by memory class instead of dumped into one generic store | — Pending |
| Keep major agent handoffs visible in chat and auditable in the control panel | User trust and debugging improve when important routing events are exposed | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-11 after initialization*
