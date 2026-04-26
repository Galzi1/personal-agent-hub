# Personal Agent Hub

## What This Is

Personal Agent Hub is a personal AI-agent system for non-coding personal and business work. It is meant to monitor AI developments, surface useful resources, generate post ideas, and support future research workflows; v1 starts with a Discord-delivered daily AI news feed that filters the highest-signal updates about new models, notable product changes in tools like Claude Code and Cursor, interesting new AI tools, and hot trends.

## Core Value

Deliver a high-signal, low-noise AI intelligence feed early enough to be useful, instead of making the user hunt through repetitive posts after everyone else has already amplified them.

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] Deliver a daily AI news digest to Discord for a single user.
- [ ] Prioritize relevance over volume by filtering low-signal items and collapsing duplicate coverage of the same update.
- [ ] Cover new model releases, important updates in AI coding tools, interesting new AI tools, and hot trends.
- [ ] Keep major agent handoffs and completions visible in chat and traceable in the control panel.
- [ ] Build on a local-first agent foundation that can later expand into resource discovery, post-idea generation, and competitor, prospect, or partner research.

### Out of Scope

- Multi-user collaboration in v1 - the first release is only for the project owner.
- A full worker mesh across every planned workflow - prove one visible end-to-end workflow before expanding.
- Software-development automation as the primary product goal - the system is for personal and business intelligence work, not coding workflows.
- Broad multi-channel delivery at launch - Discord is the first delivery surface; other channels can follow later.
- Full competitor, prospect, and partner research automation in v1 - valuable later, but not part of the first proof point.

## Context

- The current workflow is manual: tracking AI news through LinkedIn, Chrome's new-tab feed, and WhatsApp communities.
- The main pain is noise: the same update appears repeatedly across sources, and discovery is reactive enough that the user often hears about items after many other people have already posted about them.
- Existing architecture notes point toward MicroClaw as the system foundation, with OpenRouter-hosted LLM access (per-task model selection via `config/models.yaml`), shared storage, observability, and a control panel on Windows. *(LLM layer revised 2026-04-24: Ollama local chat/embeddings path dropped after Plan 00-01 confirmed infeasibility under 6.4 GB free RAM; see Phase 0 CONTEXT.md D-13 through D-22.)*
- The current design direction favors visible routing: major handoffs and completions should appear in chat, while the control panel remains the forensic layer for traces and low-level state.
- The current memory direction is layered memory: agent-local durable memory plus a smaller shared project memory, with explicit promotion of validated wins.
- The initial product slice should prove one visible workflow, then grow into adjacent personal and business workflows such as resource discovery, post ideas, and market research.

## Constraints

- **Platform**: Windows-first foundation around MicroClaw (validated 2026-04-23) + OpenRouter API for LLM tasks - existing architecture work originally assumed local Ollama; revised 2026-04-24.
- **Delivery**: Discord-first for v1 - the digest must arrive where the user already wants to consume it.
- **Audience**: Single-user initial release - no v1 need for shared roles, permissions, or client-facing behavior.
- **Signal Quality**: Relevance and deduplication matter more than raw coverage - reducing noise is a success condition, not a nice-to-have.
- **Architecture**: Major handoffs must stay visible in chat and auditable in the control panel - trust and debugging depend on this.
- **Scope**: Prove one end-to-end workflow before expanding worker taxonomy or channel coverage - avoid overbuilding the full architecture upfront.
- **Planning Guard**: No new planning artifacts until the current phase's first plan is implemented and passing tests (R6 mitigation).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use MicroClaw as the system foundation | Matches architecture direction: OpenAI-compatible LLM provider layer (used for OpenRouter), Windows support, control plane, first-class sub-agents | Validated 2026-04-23 (Plan 00-01 GO) |
| Start with a Discord-delivered daily AI news feed | One visible, high-value workflow is a better first proof point than building the full worker mesh | - Pending |
| Optimize for high-signal relevance over maximum coverage | The user's biggest pain is noisy duplicate reporting and reactive discovery | - Pending |
| Treat the product as a personal and business task hub, not a coding agent | The intended value is AI intelligence, resource discovery, idea generation, and research support | - Pending |
| Use layered memory with agent-local and shared project memory | Durable context should be curated by memory class instead of dumped into one generic store | - Pending |
| Keep major agent handoffs visible in chat and auditable in the control panel | User trust and debugging improve when important routing events are exposed | - Pending |
| Run validation spikes before Phase 1 implementation | Risk review identified MicroClaw (R1), LLM model quality (R3), and watchlist coverage (R4) as testable unknowns that should be resolved early | Phase 0 added to roadmap; R1 CLOSED 2026-04-23; R3 under evaluation via Plan 00-02 |
| Add thin digest milestone after Phase 1 | Risk review identified motivation attrition from long time to first useful digest (R2) as a high risk | Phase 2 added to roadmap |
| Enforce planning-to-execution ratio guard | Risk review identified over-planning relative to execution (R6) - no new planning artifacts until current phase first plan is implemented and passing | Active constraint |

## Risks

A formal risk review was conducted on 2026-04-12. Full risk register: `.planning/RISK-REVIEW.md`.

**Critical risks actively mitigated by roadmap structure:**
- ~~**R1:** MicroClaw as single point of failure~~ - **CLOSED 2026-04-23** via Plan 00-01 GO
- **R2:** Long time to first useful digest - Phase 2 thin digest milestone
- **R3:** OpenRouter-hosted model quality uncertainty - Phase 0 Plan 00-02 evaluation spike

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
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-24 - OpenRouter pivot post Plan 00-01 GO (see Phase 0 CONTEXT.md D-13 through D-24)*
