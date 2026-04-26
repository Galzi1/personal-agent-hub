# Research Summary

**Project:** Personal Agent Hub  
**Scope:** v1 personal AI-intel workflow for a single user, delivered in Discord  
**Synthesized:** 2026-04-11

## Executive Summary

Personal Agent Hub should be built as a **workflow-first personal intelligence system**, not a generic autonomous agent platform. For v1, the product is a **single reliable daily AI digest** that ingests a curated set of high-yield sources, normalizes and clusters duplicate coverage into canonical stories, ranks those stories for this user's priorities, and delivers a short Discord brief with citations and visible workflow handoffs. The research is consistent that the main risk is **signal quality**, not orchestration breadth.

The recommended implementation is a **Windows-first local monolith** on **MicroClaw v0.1.50 + Ollama v0.20.5**, with **SQLite + sqlite-vec** as the only database and small **Python 3.12 + uv** sidecars for ingestion, extraction, and ranking utilities. The architecture should keep one explicit digest workflow with bounded services for intake, normalization, deduplication, ranking, composition, feedback, and memory promotion. Major handoffs should stay visible in Discord and auditable in the control panel from the same event log.

The biggest delivery risks are predictable: too many low-quality sources, weak story-level deduplication, popularity-driven ranking, late ingestion despite a daily cadence, and memory pollution from promoting noisy observations. Mitigation is also clear: start with curated primary sources, treat **canonical story formation** as a first-class subsystem, use explicit ranking dimensions tied to user relevance, separate ingestion cadence from delivery cadence, and keep durable memory promotion strict and reviewable.

## Key Findings

### Stack

- **MicroClaw v0.1.50** — primary runtime, scheduler, Discord delivery, control plane, sub-agent support; use it as the core runtime, not just a wrapper.
- **Ollama v0.20.5** — local chat + embeddings runtime; use for ranking assistance, summarization, and semantic dedup support.
- **SQLite + sqlite-vec v0.1.9** — single local store for raw items, canonical stories, runs, memory metadata, and vector similarity.
- **Python 3.12 + uv 0.11.6** — sidecars/utilities for RSS ingestion, extraction, fuzzy matching, and custom MCP tools.
- **feedparser + httpx + trafilatura + pydantic + rapidfuzz** — default ingestion/normalization toolchain.
- **Apify MCP** — fallback only for hard sources; do not make browser scraping the default path.
- **Discord via MicroClaw native support** — avoid a separate bot framework unless native delivery proves insufficient.

**Critical version/build requirements**
- Build MicroClaw with `sqlite-vec` support enabled.
- Keep Ollama on the verified `v0.20.x` line.
- Prefer Python 3.12 on Windows for smoother package compatibility.

### Must-have v1 Features

- **Curated multi-source collection** from official blogs, changelogs, selected newsletters, Google News/RSS, and a few high-value community sources.
- **Topic/profile targeting** for model releases, AI coding tools, useful new AI tools, and hot trends.
- **Story-level deduplication and clustering** across overlapping coverage.
- **Relevance ranking** that outputs a short, high-signal daily shortlist.
- **Discord digest composition** with concise sections, citations, and a short **“why it matters”** explanation per item.
- **Basic feedback controls**: mute source, mute topic, thumbs up/down.
- **Run visibility** in chat plus auditable traceability in the control panel.

### Launch-critical vs later

**Launch-critical**
- Source intake
- Canonical item/story model
- Deduplication/clustering
- Relevance ranking
- Discord digest with citations
- Run visibility
- Basic feedback/suppression

**Later (v1.x)**
- Novelty / first-seen scoring
- Personalized taste memory
- Trend rollups across days
- One-click downstream actions like “save as resource” or “turn into post idea”

**Later (v2+)**
- Structured intel workspace for companies/tools/models
- Competitor/prospect/partner monitoring briefs
- Post-idea generation workflow
- Selective urgent alerts

### Architecture

**Recommended shape**
- One **workflow-oriented local monolith**
- One **explicit digest workflow**
- Bounded services instead of a broad worker mesh
- Append-only audit/event log as the shared source of truth

**Major components**
- **Scheduler / run orchestrator** — owns run state and step order.
- **Routing/policy layer** — decides what becomes visible in Discord.
- **Source intake** — fetches and stores raw source items.
- **Normalizer** — converts items into a common schema.
- **Dedup/cluster service** — forms canonical stories.
- **Rank/filter service** — scores signal using rules plus LLM judgment.
- **Digest composer** — drafts digest sections and item summaries.
- **Discord adapter** — posts digest and captures feedback.
- **Feedback + memory promotion** — promotes only validated durable preferences/patterns.
- **Event log / control panel** — exposes runs, decisions, and failures.

**Key patterns**
- Orchestrated pipeline, not open-ended swarm.
- Canonical **story** as the primary domain object.
- Shared event stream for both chat visibility and control-panel traces.
- Promotion-based layered memory: logs are not memory.

### Highest-risk Pitfalls

1. **Adding too many sources too early**  
   Prevent with source tiers, primary-source weighting, and per-source usefulness metrics.
2. **Weak dedup that only matches URLs/titles**  
   Prevent with story/event clustering before ranking and by preserving one canonical record plus supporting references.
3. **Ranking popularity instead of user relevance**  
   Prevent with explicit scoring for relevance, novelty, credibility, actionability, freshness, and duplicate-adjusted momentum.
4. **Daily delivery that is still too late**  
   Prevent by separating ingestion cadence from delivery cadence and tracking first-seen vs delivered lag.
5. **Invisible routing or unexplained selections**  
   Prevent by attaching provenance and selection rationale to every digest item and surfacing major handoffs in chat.
6. **Memory pollution**  
   Prevent with strict promotion rules, TTL/review policies, and stricter shared-memory admission than agent-local memory.

## Implications for Roadmap

### Suggested phase structure

#### Phase 1 — Foundation, traceability, and curated ingestion
- **Why first:** trust and debugging depend on observable runs; freshness and provenance need to exist before quality tuning.
- **Delivers:** MicroClaw + Ollama wiring, Discord outbound delivery, scheduler/manual trigger, run IDs, event log, basic control-panel traceability, curated source connectors, raw-item persistence, provenance model.
- **Features covered:** multi-source collection, run visibility, visible routing.
- **Pitfalls to avoid:** overbuilding the worker mesh, too many low-quality sources, invisible routing, missing freshness instrumentation.

#### Phase 2 — Canonical story pipeline
- **Why second:** deduplication is the core moat for this product’s stated pain.
- **Delivers:** normalized item schema, canonical story model, story clustering, duplicate-collapse logic, confidence on merges.
- **Features covered:** deduplication/clustering, explainability foundation, launch-critical data model.
- **Pitfalls to avoid:** document-level dedupe only, losing source provenance, summarizing before verification, no uncertainty/state model.

#### Phase 3 — Ranking and digest composition
- **Why third:** only worth tuning once inputs are trustworthy.
- **Delivers:** topic targeting, scoring rubric, digest selection, Discord formatting, citations, “why it matters” synthesis.
- **Features covered:** topic/profile targeting, relevance ranking, digest composition, explainability/citations.
- **Pitfalls to avoid:** popularity-based ranking, entertaining-but-not-actionable content, unreadable Discord output, unverifiable summaries.

#### Phase 4 — Feedback and memory promotion
- **Why fourth:** personalization matters after the baseline digest is consistently useful.
- **Delivers:** thumbs up/down, mute topic/source, ranking explanation capture, agent-local memory, stricter shared-memory promotion rules.
- **Features covered:** feedback/suppression, early personalized calibration.
- **Pitfalls to avoid:** over-personalizing too early, memory pollution, storing transient judgments as durable memory.

#### Phase 5 — Quality loop and near-term expansion
- **Why fifth:** expand only after the daily digest is measurable and trusted.
- **Delivers:** quality metrics/review loop, novelty scoring, trend rollups, optional downstream actions, reusable workflow primitives for adjacent briefs.
- **Features covered:** novelty scoring, trend rollups, initial adjacent workflow support.
- **Pitfalls to avoid:** prompt thrash without metrics, platform expansion before one workflow is proven.

### Research flags

**Likely needs deeper phase research**
- **Phase 2:** canonical story clustering, confidence models, uncertainty/state transitions.
- **Phase 3:** ranking rubric design, digest UX tuning, freshness thresholds, “why it matters” prompting.
- **Phase 5:** novelty scoring and trend detection once real data exists.

**Well-understood / can proceed without extra research**
- **Phase 1:** MicroClaw/Ollama/SQLite foundation, Discord-first delivery, event logging, curated RSS/API-first ingestion.
- **Phase 4:** basic feedback controls and strict memory-promotion rules.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Strong alignment between project constraints and researched stack choices; versions are specific and practical. |
| Features | MEDIUM | Feature priorities are coherent, but some differentiators will need validation against real user behavior. |
| Architecture | MEDIUM-HIGH | The workflow-first architecture is strongly supported by the project’s scope and risks. |
| Pitfalls | MEDIUM | Risks are credible and project-specific, but some depend on real production usage to validate severity. |

**Overall confidence:** MEDIUM-HIGH

## Gaps to Address During Planning

- Define the **initial curated source list** and source-tier policy explicitly.
- Specify the **canonical story schema**, including confidence/state fields such as observed, corroborated, confirmed, disputed, superseded.
- Define the **ranking rubric** numerically enough to evaluate regressions.
- Decide the **daily delivery time** and the ingestion cadence needed to preserve freshness.
- Define the **quality scorecard** for v1: duplicate-collapse rate, freshness lag, user-marked hits, ignored items, and missed major stories.
- Clarify the exact **Discord feedback UX**: reactions, buttons, commands, or a mix.

## Sources

- `.planning/PROJECT.md`
- `.planning/research/STACK.md`
- `.planning/research/FEATURES.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`
- Underlying cited sources aggregated from those files, including MicroClaw, Ollama, sqlite-vec, Apify MCP, Feedly, and relevant internal architecture notes.
