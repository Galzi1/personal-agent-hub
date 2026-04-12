# Roadmap Risk Review — Personal Agent Hub

**Reviewed:** 2026-04-12
**Scope:** Full roadmap (4 phases), excluding individual sub-phase plans in Phase 1
**Overall Risk Level:** Moderate-High

---

## 1. Plan Summary

**Purpose in one sentence:** Deliver a local-first, daily AI-news digest to Discord for a single user by building a four-phase pipeline: curated intake → canonical story formation → ranked digest composition → feedback-driven calibration.

**Key components touched:**
- **Runtime:** MicroClaw v0.1.50 (Rust) as the execution core, scheduler, and Discord delivery surface
- **LLM:** Ollama v0.20.5 for local chat, ranking assistance, summarization, and embeddings
- **Storage:** SQLite + sqlite-vec for raw items, canonical stories, run events, memory
- **Sidecars:** Python 3.12 + uv for ingestion, extraction, fuzzy matching, and MCP utilities
- **Delivery:** Discord (digest channel + agent-status side channel)
- **Observability:** Append-only event log, control-panel trace surface, visible routing in chat
- **Sources:** RSS/Atom/GitHub release feeds from a curated watchlist with trust tiers

**The plan's stated assumptions:**
- MicroClaw can handle scheduling, Discord delivery, control plane, sub-agents, and SQLite persistence natively
- Ollama is sufficient for local LLM tasks in v1
- A single-user, single-workflow proof point is the right starting posture
- Signal quality and dedup are the real hard problems, not orchestration scale
- Visible routing builds trust; hidden agent internals erode it

**Theory of success:** If the team can reliably ingest from curated sources, collapse duplicates into canonical stories, rank for relevance, and deliver a scannable Discord brief — all with visible run status — the product solves the stated pain of noisy, late, repetitive AI-news consumption. Each subsequent phase layers on intelligence (dedup, ranking, feedback) that compounds the value of the foundation.

---

## 2. Assumptions & Evidence

### A1: MicroClaw v0.1.50 is production-ready enough to serve as the sole runtime
- **Type:** Foundational, implicit
- **Evidence:** MicroClaw has 643 GitHub stars. The README verifies Discord support, scheduled tasks, MCP, SQLite persistence, sub-agent lifecycle, and Ollama support. Version 0.1.50 was published 2026-04-11.
- **Justification status:** WEAK. A v0.1.x release with 643 stars is pre-1.0 software. The research documents note the "maturity risk" and recommend forking early, but the roadmap does not include any spike or fallback timeline for MicroClaw proving insufficient.
- **If wrong:** The entire four-phase plan collapses. Every phase depends on MicroClaw for scheduling, Discord delivery, the control plane, and the event log. There is no NanoClaw fallback plan with concrete triggers or timelines.
- **Testable?** Yes (secret). A focused spike on MicroClaw's scheduler reliability, Discord message posting, and SQLite persistence under daily-run conditions could validate this within days.

### A2: Ollama local models are good enough for ranking, dedup assistance, and digest summarization
- **Type:** Structural, partially explicit
- **Evidence:** The STACK.md notes the variant "If local models are not good enough for final digest writing" and suggests adding a remote provider only for final synthesis. But the roadmap itself does not budget for this variant — there is no plan or phase allocation for evaluating local model quality.
- **Justification status:** MODERATE. Ollama's API surface is verified, but model quality for domain-specific ranking and "why it matters" synthesis on local hardware is unverified.
- **If wrong:** Phases 2 and 3 (canonical story formation and ranked digest composition) produce low-quality output. The user gets a digest that is technically correct but reads poorly or makes bad ranking decisions. This may not be obvious until late in Phase 3.
- **Testable?** Yes (secret). Run a handful of representative ranking and summarization tasks against the target Ollama model before committing to Phase 2 implementation.

### A3: A curated 8-9 source watchlist provides enough coverage to be useful
- **Type:** Structural, explicit
- **Evidence:** The research recommends starting small and expanding. The starter watchlist includes OpenAI, DeepMind, Cursor, Claude Code, VS Code Copilot, Ollama releases, TestingCatalog, Simon Willison, and Latent Space.
- **Justification status:** MODERATE. The watchlist is well-reasoned, but it is entirely RSS/Atom — meaning any major AI development that breaks first on X/Twitter, Discord communities, or press outlets without feeds will be missed entirely until Phase 1 is expanded.
- **If wrong:** The digest feels incomplete. The user still discovers important news elsewhere, undermining the core value proposition of "earlier than manual scrolling."
- **Testable?** Yes (secret). Backtest the watchlist against one week of actual AI news the user cared about and measure what was covered vs. missed.

### A4: Deduplication can be meaningfully solved at the story level
- **Type:** Foundational, explicit
- **Evidence:** The architecture and pitfalls research correctly identify this as the core hard problem. Phase 2 is dedicated to it. The approach combines fuzzy title matching (rapidfuzz), embeddings (sqlite-vec), and canonical story clustering.
- **Justification status:** MODERATE. The tools are appropriate, but the plan assumes that story-level clustering is solvable with these tools at sufficient quality. Real-world AI news dedup is hard because the "same event" is often discussed from wildly different angles (technical, business, opinion) with different titles.
- **If wrong:** Digests remain noisy despite the pipeline being technically correct. The user's core pain persists.
- **Testable?** Partially (secret for simple cases, mystery for edge cases). Simple duplicate collapse is testable against recorded feeds. Whether the system correctly merges "Anthropic releases Claude 4" from an official blog post with "Claude 4 benchmark analysis" from a trend-watcher is a harder judgment call.

### A5: The four-phase sequence is the right build order
- **Type:** Structural, explicit
- **Evidence:** The architecture research provides a clear rationale: you cannot rank what you haven't ingested, you cannot compose what you haven't ranked, and you cannot learn from feedback until the baseline works. This is sound.
- **Justification status:** STRONG for the ordering. But there is an implicit assumption that Phase 1 delivers enough stand-alone value to sustain motivation. Phase 1's output is "candidate updates gathered + observable run status" — the user does not actually get a useful digest until Phase 3 is complete. That means the user endures 3 full phases of building before the product delivers its core promise.
- **If wrong:** Motivation attrition. Three phases of infrastructure work before a useful daily digest creates a long feedback desert.

### A6: SQLite is sufficient for all storage needs in v1
- **Type:** Peripheral, explicit
- **Evidence:** For a single-user local system running once daily, SQLite is more than adequate for raw items, stories, events, and memory metadata.
- **Justification status:** STRONG. This is well-justified.
- **If wrong:** Minor — migration to PostgreSQL is a known path.

### A7: Discord is the right delivery surface and MicroClaw's native Discord support is sufficient
- **Type:** Structural, explicit
- **Evidence:** The user chose Discord as the consumption surface. MicroClaw's README confirms Discord support including long-message splitting.
- **Justification status:** MODERATE. Discord delivery is the user's preference. Whether MicroClaw's native support handles embeds, buttons (for feedback), and rich formatting well enough is unverified.
- **If wrong:** Phase 3 (digest formatting) and Phase 4 (feedback controls via Discord reactions/buttons) may require falling back to discord.py, adding a second delivery dependency.

### A8: A single daily run at 08:00 is the right cadence
- **Type:** Structural, explicit
- **Evidence:** The user chose this. The pitfalls research warns about freshness lag but the plan separates ingestion cadence from delivery cadence only as a future consideration, not in Phase 1.
- **Justification status:** MODERATE. A single daily poll at run time means the 08:00 digest contains whatever was published since the last run — up to 24 hours of latency. For fast-moving AI news (model launches often happen US afternoon/evening), an 08:00 run may miss items published the previous evening that are already widely known by morning.
- **If wrong:** The digest feels late, exactly the problem it was designed to solve. The pitfalls doc explicitly warns about this (Pitfall 4).

### A9: The Windows-first constraint does not create meaningful friction
- **Type:** Structural, implicit
- **Evidence:** MicroClaw claims native Windows support. Python 3.12 works on Windows. uv works on Windows.
- **Justification status:** MODERATE. The research notes uv version mismatch (0.8.13 installed vs 0.11.6 needed) and Ollama is missing from the local machine. More importantly, Rust-based tools on Windows sometimes have edge cases with path handling, process management, and signal handling that don't surface until production use.
- **If wrong:** Debugging Windows-specific issues in a pre-1.0 Rust runtime (MicroClaw) could consume significant Phase 1 time.

### A10: The project is a solo effort with sufficient bandwidth
- **Type:** Implicit (no team mentioned anywhere)
- **Evidence:** Single-user product, personal project, no mention of other contributors.
- **Justification status:** ASSUMED. If this is a solo project, the four-phase roadmap represents a significant time commitment. The plan does not discuss time horizons, but the volume of planning artifacts suggests ambition that may exceed available bandwidth.
- **If wrong:** N/A — but the risk is that scope exceeds capacity, not that the assumption is wrong.

---

## 3. Ipcha Mistabra — Devil's Advocacy

### 3a. The Inversion Test

**Claim: "MicroClaw as the sole runtime simplifies the architecture."**
*Inversion: MicroClaw as the sole runtime creates a single point of failure and vendor lock-in to a pre-1.0 project.*

This inversion is uncomfortably compelling. The entire roadmap — scheduling, Discord delivery, control plane, event logging, sub-agents, MCP integration — routes through one v0.1.x Rust binary with 643 stars. If MicroClaw has a blocking bug in its scheduler, or its Discord adapter doesn't support embeds needed for Phase 3, or its SQLite layer has a data-corruption edge case, the project must either fix upstream Rust code or rewrite significant portions. The architecture mapping document says "fork early, own the codebase" as mitigation, but forking a Rust project the developer may not deeply understand is not free.

**Claim: "Starting with a small curated watchlist and expanding later is the right approach."**
*Inversion: Starting too small means the digest is useless for weeks, and the user never builds the habit of checking it.*

If the 08:00 digest regularly contains 0-2 items because 9 RSS feeds don't produce enough daily content, the product's core feedback loop never activates. The user stops checking Discord, and expansion comes too late to recover the habit. The pitfalls doc warns about coverage gaps but the plan's design explicitly accepts this risk without defining a minimum-viable-item-count threshold.

**Claim: "Four sequential phases is the right structure."**
*Inversion: Four sequential phases means the user gets no useful digest for 3 phases — by then, interest may have evaporated.*

Phase 1 delivers observable runs but no digest. Phase 2 delivers canonical stories but still no digest. The user's actual daily value starts at Phase 3. If each phase takes 2-4 weeks (conservatively), the user is 6-12 weeks from a working product. For a personal project, this is a long time to build infrastructure without experiencing the core value loop.

### 3b. The Little Boy from Copenhagen

**A new engineer joining the project would ask:** "Why is there a 350-line architecture document and a 430-line pitfalls document for a personal RSS reader with 9 feeds?" The planning-to-code ratio is extremely high. Zero lines of application code exist. The risk of over-planning a personal project is that the planning artifacts become the product instead of the software.

**An SRE on-call at 3 AM would ask:** "What happens when MicroClaw crashes at 07:55?" The plan specifies one automatic retry, but there is no monitoring, no alerting (other than a Discord failure message), and no health check. For a personal project this is fine — but it means the "observable run status" promise depends entirely on the user remembering to check the status channel.

**A product manager would ask:** "What is the minimum viable version of this product?" The roadmap implicitly defines MVP as "Phase 4 complete" (all 13 requirements met). But a more aggressive MVP might be: "Phase 1 + a simple summarization step that posts raw/lightly-formatted items to Discord" — delivering some daily value in weeks instead of months, then iterating quality.

**A user who doesn't read changelogs would ask:** "I just want to know what happened in AI today. Why do I need to understand run IDs, event timelines, and trace links?" The plan heavily emphasizes observability and traceability (Phases 1 and much of Phase 1's 4 sub-plans), which is excellent engineering but may be over-indexed for a single-user personal tool where the user is also the operator.

### 3c. Failure of Imagination Check

**Scenario 1: MicroClaw is abandoned or stalls.** The project is at v0.1.50. What if the maintainer loses interest? The roadmap locks into MicroClaw so deeply that migrating away would require rewriting scheduling, Discord delivery, the control plane, and the event system. The "fork and own" mitigation assumes the user can maintain a Rust codebase.

**Scenario 2: RSS feeds change or disappear.** The starter watchlist depends on specific feed URLs. If OpenAI restructures their blog, or Cursor drops their Atom feed, or GitHub changes their releases.atom format, the ingestion layer breaks silently. The plan does not describe feed health monitoring beyond "source.fetch.failed" events.

**Scenario 3: The AI news landscape shifts.** The product targets a specific moment in AI: rapid model releases, coding tool churn, and tool proliferation. If the AI news cycle slows down (consolidation, regulatory pause), the daily digest may routinely have nothing worth reporting. Conversely, if the news cycle accelerates further, 9 RSS feeds become hopelessly inadequate.

**Scenario 4: Local Ollama models plateau while cloud models leap ahead.** The plan uses Ollama for ranking, dedup assistance, and summarization. If local models remain qualitatively worse than cloud alternatives for these specific tasks, the product's output quality has a permanent ceiling that competing cloud-based tools (like Feedly AI) don't share.

---

## 4. Risk Register

| ID | Category | Description | Trigger | Prob | Severity | Priority | Detection | Mitigation | Contingency | Assumption |
|----|----------|-------------|---------|------|----------|----------|-----------|------------|-------------|------------|
| **R1** | Technical | **MicroClaw proves insufficient or breaks** — blocking bug in scheduler, Discord adapter, or SQLite layer that cannot be worked around | Any Phase 1 implementation task that exercises an undocumented or edge-case MicroClaw behavior | Medium | Critical | **Critical** | Implementation fails to complete a planned feature; Discord messages don't post; scheduler skips runs | Run a focused MicroClaw spike before committing to Phase 1 implementation: test scheduling, Discord posting, SQLite persistence, and the control plane on Windows | Fall back to NanoClaw (requires WSL2) or assemble a custom stack from discord.py + APScheduler + SQLite | A1 |
| **R2** | Schedule | **Long time to first useful digest** — user motivation attrition during 3 phases of infrastructure before the product delivers daily value | Phase 2 begins with no digest ever having been delivered to Discord | High | High | **High** | The user stops checking Discord; enthusiasm wanes; the project stalls | Consider a "thin slice" variant: after Phase 1 ingestion works, add a minimal summarization step that posts raw/lightly-formatted items to Discord, then iterate quality | Accept a lower-quality early digest as a scaffold; formalize this as Phase 1.5 or a plan within Phase 1 | A5 |
| **R3** | Technical | **Local Ollama model quality is insufficient** for ranking, dedup assistance, or digest summarization | Phase 2/3 implementation produces outputs that are noticeably worse than manual curation | Medium | High | **High** | Digest items are poorly ranked, summaries are generic or hallucinated, dedup merges wrong items | Evaluate target Ollama model on representative tasks before Phase 2 starts; define quality thresholds | Add a remote model provider (OpenAI/Anthropic API) for the final synthesis step only, as STACK.md suggests | A2 |
| **R4** | Operational | **Watchlist coverage too narrow** — daily digest routinely has 0-2 items, failing to be useful | Phase 1 is complete but most daily runs produce "no qualifying items" | Medium | Medium | **High** | Frequent "completed_no_items" run outcomes; user stops checking | Define a minimum daily item target; backtest the watchlist against one week of real AI news before committing | Expand the watchlist aggressively; add curated Twitter/X list scraping via Apify as a near-term source class | A3 |
| **R5** | Technical | **Deduplication quality is inadequate** — story-level clustering merges wrong items or misses obvious duplicates | Phase 2 implementation tested against real feeds | Medium | High | **High** | User says "you already told me this" or "these are different things, not the same story" | Build a test corpus of known duplicate/non-duplicate AI news items; iterate clustering thresholds against it | Accept looser dedup with manual override capability; or escalate to a cloud embedding model for better semantic similarity | A4 |
| **R6** | Schedule | **Over-planning relative to execution** — the project generates planning artifacts faster than working software | Week 2+ with no application code written; planning documents continue to grow | Medium | Medium | **Medium** | No code exists in the repo; new planning documents keep appearing | Set a hard deadline: no new planning documents until Phase 1 Plan 01-01 is implemented | Timebox planning to a fixed percentage of each phase | A10 |
| **R7** | Operational | **Windows-specific runtime issues** with MicroClaw, Ollama, or Python tooling | Phase 1 implementation encounters path handling, process management, or signal handling bugs on Windows | Medium | Medium | **Medium** | Build failures, test failures, or runtime crashes that don't reproduce on Linux | Test MicroClaw and Ollama on the actual Windows machine before starting Phase 1 | Use WSL2 as a runtime environment (contradicts Windows-first constraint but unblocks progress) | A9 |
| **R8** | Technical | **Discord delivery limitations** — MicroClaw's native Discord support lacks embeds, buttons, or formatting needed for Phases 3-4 | Phase 3 (digest formatting) or Phase 4 (feedback reactions/buttons) implementation | Medium | Medium | **Medium** | Required Discord features are not available through MicroClaw's API | Test MicroClaw Discord capabilities for embed formatting and interactive elements early in Phase 1 | Fall back to discord.py sidecar for delivery, keeping MicroClaw for scheduling and orchestration | A7 |
| **R9** | Operational | **Digest freshness lag** — 08:00 daily digest contains stale news the user already saw | Major AI announcement happens at 18:00 local time; user hears about it on social media by 20:00; digest arrives 12 hours later | High | Medium | **Medium** | User reaction: "I already knew all of this" | Separate ingestion cadence from delivery cadence early; consider a second evening polling pass | Add selective "breaking news" alerts for high-confidence major events (but this is explicitly out of scope for v1) | A8 |
| **R10** | Technical | **Feed URL instability** — RSS/Atom feeds change URLs, formats, or disappear | A source restructures their blog or drops their feed | Low | Medium | **Low** | `source.fetch.failed` events; gradual coverage degradation | Monitor per-source fetch success rate; alert on consecutive failures | Maintain a feed URL registry that can be updated quickly; add Apify fallback for critical sources | A3 |

### Risk Classification

**Known Knowns:** R6 (over-planning), R10 (feed instability) — these are understood risks with established mitigations.

**Known Unknowns:** R1 (MicroClaw sufficiency), R3 (Ollama quality), R5 (dedup quality), R8 (Discord limitations) — we know these are risks but cannot quantify them without testing.

**Unknown Unknowns (surfaced by Ipcha Mistabra):** R2 (motivation attrition from long time to value), R9 (freshness lag undermining core value proposition), and the unregistered scenario of MicroClaw abandonment.

---

## 5. Verdict & Recommendations

### Overall Risk Level: Moderate-High

The roadmap is well-researched, architecturally coherent, and honest about its own risks. However, it has two structural vulnerabilities that deserve attention before execution begins.

### Top 3 Risks

1. **R1 — MicroClaw as a single point of failure (Critical).** The entire system depends on a pre-1.0 Rust project. A focused validation spike should happen before any implementation work begins. This is a secret, not a mystery — a few days of testing can answer it.

2. **R2 — Long time to first useful digest (High).** Three full phases before the user gets a working daily brief is too long for a personal project. The plan should include a "thin slice" milestone that delivers some daily value — even if crude — after Phase 1.

3. **R3 — Local model quality uncertainty (High).** Ollama's adequacy for ranking and summarization is assumed but unverified. This is also a secret that can be tested before it becomes a problem.

### Recommended Actions

1. **Run a MicroClaw validation spike** (1-3 days) before starting Phase 1 implementation. Test: daily scheduled task execution on Windows, Discord message posting with embeds, SQLite read/write under the run-event pattern, and control-plane accessibility. Define go/no-go criteria.

2. **Add a "thin digest" milestone** to Phase 1 or as Phase 1.5. After ingestion works, post a simple formatted list of ingested items to Discord daily. This gives the user a tangible daily artifact to react to, even before dedup and ranking exist. It also validates the end-to-end pipeline (schedule → ingest → format → deliver) early.

3. **Evaluate Ollama model quality** on 10-20 representative tasks (ranking relevance, summarizing an AI news item, explaining "why it matters") before Phase 2 planning begins. Define minimum quality thresholds. If local models fail, plan the remote-provider fallback now rather than in Phase 3.

4. **Backtest the starter watchlist** against one real week of AI news the user cared about. Count how many important items the 9 feeds would have caught vs. missed. This converts A3 from an assumption into evidence.

5. **Set a planning-to-execution ratio guard.** The project currently has ~20 planning documents and 0 lines of code. Consider a rule: no new planning artifacts until the current phase's first plan is implemented and passing tests.

### Open Questions

- **How long does the user expect each phase to take?** The roadmap has no timeline, which is fine for planning but relevant for assessing R2.
- **Has the user built anything with MicroClaw before?** If not, R1 is higher than estimated.
- **What Ollama model does the user plan to run?** Model choice significantly affects R3; a 7B model vs. a 70B model has very different quality ceilings.
- **What is the user's Rust proficiency?** The "fork and own MicroClaw" mitigation assumes ability to modify Rust code.

### What the Roadmap Does Well

1. **Honest about the hard problem.** The roadmap and supporting research correctly identify deduplication and signal quality — not orchestration — as the real challenge. This is rare and valuable.

2. **Excellent pitfall awareness.** The 12-pitfall analysis (PITFALLS.md) is specific, domain-relevant, and directly informs the phase structure. The team is not building blind.

3. **Strong architectural discipline.** The decision to start with one orchestrated workflow instead of a multi-agent swarm is the right call. The "canonical story as primary domain object" pattern is the correct abstraction.

4. **Visible routing as a first-class concern.** Treating observability as a product feature rather than an afterthought is a mature decision that will pay off in debugging and trust.

5. **Thoughtful memory design.** The layered memory model with strict promotion rules avoids the most common memory-pollution failure mode in agent systems.

6. **Clean requirement traceability.** All 13 v1 requirements are mapped to phases with no gaps. The traceability table is simple and complete.

---

*Reviewed: 2026-04-12*
*Reviewer: Claude (risk review skill)*
*Inputs: ROADMAP.md, PROJECT.md, REQUIREMENTS.md, STATE.md, ARCHITECTURE.md, STACK.md, FEATURES.md, PITFALLS.md, SUMMARY.md, 01-CONTEXT.md, 01-RESEARCH.md, 01-VALIDATION.md, 01-DISCUSSION-LOG.md, architecture-repository-mapping.md, visible-routing-architecture.md, layered-memory-model.md*
