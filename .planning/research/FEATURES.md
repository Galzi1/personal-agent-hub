# Feature Research

**Domain:** personal AI-intel / AI-news workflow for a single user
**Researched:** 2026-04-11
**Confidence:** MEDIUM

## Feature Landscape

This product is not a generic "AI assistant." The v1 job is narrower: watch the AI tooling ecosystem, cut through duplicate/noisy coverage, and deliver a small Discord digest early enough to matter. That means the core feature bar is closer to a personal intelligence system than to a news reader or chatbot.

### Table Stakes (Users Expect These)

Features users assume exist for a useful personal intel workflow. Missing these = the product does not solve the stated pain.

| Feature | Why Expected | Complexity | Major Dependencies | Notes |
|---------|--------------|------------|--------------------|-------|
| Multi-source collection | The user's current problem spans LinkedIn-like social chatter, newsletters, blogs, product updates, and search feeds. A single-source feed will miss important updates or lag badly. | MEDIUM | Source connectors, normalization pipeline | Start with high-yield sources only: official product blogs/changelogs, selected newsletters, Google News/RSS, a few social/community sources. This also unlocks future resource discovery. |
| Topic/profile targeting | A useful digest must explicitly know what counts: Claude Code, Cursor, model releases, new tools, hot trends. Otherwise it becomes generic AI news. | LOW | Configurable watchlist/taxonomy | Seed with a curated topic map: tools, model vendors, product names, trend buckets, exclusions. This later unlocks competitor/prospect/partner monitoring. |
| Deduplication + clustering | This is the core pain. Repeated coverage of the same launch across many sources is noise, not value. | HIGH | Content normalization, similarity matching, canonical item model | Must collapse "same event, many posts" into one item with supporting links. Feedly documents both deduplication and clustering as first-class capabilities; this is table stakes for this domain. |
| Relevance ranking / digest selection | Collection without ranking just recreates the firehose. The product must decide what deserves inclusion in a daily brief. | HIGH | Topic targeting, quality scoring, recency, dedup | Optimize for a short list of meaningful items, not maximum recall. This is the main anti-noise control. |
| Digest composition for Discord | The user wants consumption in Discord, not another dashboard. The digest must be readable, skimmable, and link back to sources. | MEDIUM | Selection pipeline, formatting, Discord delivery | Include headline, why it matters, source links, and grouped sections (models, coding tools, new tools, trends). |
| Explainability / citations | A personal intel system must show why an item was included and where it came from, or trust collapses fast. | MEDIUM | Source provenance, summarization with references | Each digest item should preserve supporting links and ideally note why it matched the watchlist. This later supports research workflows. |
| Feedback and suppression controls | The user needs a fast way to say "more like this," "less like this," or "never show this source/topic again." Without this, noise never improves. | MEDIUM | Stable item IDs, preference storage, memory/promotion policy | Minimum version: mute source, mute topic, and thumbs up/down on digest items. This aligns with the layered-memory direction. |
| Run visibility / failure visibility | If the digest is late, empty, or thin, the user needs to know whether nothing happened or the workflow failed. | MEDIUM | Visible routing events, run logs, notification surface | Because the project explicitly favors visible routing, major workflow start/completion/failure should be visible in chat, with deeper traces elsewhere. |

### Differentiators (Competitive Advantage)

Features that make this feel better than a news reader, RSS app, or generic AI summary bot.

| Feature | Value Proposition | Complexity | Major Dependencies | Notes |
|---------|-------------------|------------|--------------------|-------|
| Novelty / first-seen scoring | Solves the "I only hear about it after everyone else" pain. Prioritizes genuinely new developments over already-saturated conversation. | HIGH | Timestamping, source weighting, canonical event model | Strong differentiator, but not required for v1 launch if daily digest quality is already high. |
| "Why this matters" synthesis | Turns raw links into usable intel by explaining the implication: model capability jump, tool workflow change, pricing shift, ecosystem signal. | MEDIUM | Summarization, source grounding, domain prompts | This matters more than generic summaries. It also directly unlocks post-idea generation later. |
| Persistent personalized taste memory | The system should learn recurring preferences: trusted sources, over-covered topics, favorite tooling categories, ignored hype cycles. | HIGH | Feedback loop, layered memory, promotion rules | This is where the system starts feeling like a personal agent instead of a static filter. Also useful for future adjacent workflows. |
| Trend rollups across days | Instead of isolated items, detect "this theme is accelerating" across several days of signals. | HIGH | Clustering, entity/topic histories, time windows | Better as v1.x. Strong fit for "hot trends" and later competitor/prospect research. |
| Structured intel objects | Store each important item as a reusable object: company, product, model, launch, source, evidence, tags. | HIGH | Canonical data model, extraction, storage | This is the biggest feature that unlocks future workflows: resource discovery, post-idea generation, and competitor/prospect/partner research. |
| One-click downstream actions | Let the user mark a digest item as "save as resource," "turn into post idea," or "watch this company/tool." | MEDIUM | Structured intel objects, memory, action routing | Not needed for initial validation, but high leverage once digest quality is proven. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that sound attractive but would actively hurt this product at the current stage.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time alert firehose | Feels faster and more "agentic" than a daily digest. | Recreates the exact noise problem; constant pings destroy signal discipline. | Keep daily digest as default. Add selective urgent alerts later only for very high-confidence, high-importance events. |
| Multi-channel delivery from day one | Sounds flexible: Discord, email, Telegram, WhatsApp, web app, etc. | Spreads effort across formatting, delivery, and state sync before proving signal quality. | Nail Discord first; add channels only after digest quality is validated. |
| Full autonomous social posting | Feels like a natural extension once summaries exist. | Expands scope into brand/tone/risk management before the core intel workflow is trusted. | Support saving post ideas first, not automatic publishing. |
| Open-ended chatbot as primary UX | Feels expected in AI products. | Encourages broad, fuzzy usage and distracts from the repeatable monitoring workflow. | Keep the product workflow-first: collect → rank → digest → feedback. Add narrow follow-up query UX later if needed. |
| Multi-user collaboration / permissions | Seems like future-proofing. | Adds roles, shared state, and workflow complexity irrelevant to a single-user v1. | Stay personal-first; revisit only when a second real user exists. |

## Feature Dependencies

```text
Source connectors
    └──requires──> Source normalization
                         └──requires──> Canonical item model
                                              ├──requires──> Deduplication / clustering
                                              ├──requires──> Relevance ranking
                                              └──requires──> Digest composition

Topic/profile targeting ──enhances──> Relevance ranking
Feedback + mute controls ──enhances──> Topic/profile targeting
Feedback + mute controls ──enhances──> Personalized taste memory

Source provenance ──requires──> Explainability / citations
Explainability / citations ──enhances──> User trust in digest

Canonical item model ──unlocks──> Structured intel objects
Structured intel objects ──unlocks──> Resource discovery
Structured intel objects ──unlocks──> Post-idea generation
Structured intel objects ──unlocks──> Competitor / prospect / partner research

Visible workflow events ──enhances──> Run visibility / failure visibility

Real-time alert firehose ──conflicts──> High-signal, low-noise positioning
```

### Dependency Notes

- **Deduplication requires normalization and a canonical item model:** the system must compare standardized items, not raw source payloads.
- **Relevance ranking depends on topic targeting:** the system cannot prioritize well if it does not know the watchlist and exclusion set.
- **Feedback is only valuable with stable item/source/topic identities:** otherwise the system cannot learn durable preferences.
- **Explainability depends on provenance retention:** if source links and match reasons are lost during summarization, trust is lost too.
- **Structured intel objects are the main future-workflow unlock:** without them, later workflows become prompt-heavy one-offs instead of reusable intelligence operations.

## MVP Definition

### Launch With (v1)

- [ ] Multi-source collection from a small curated source set — essential to escape single-feed blind spots
- [ ] Topic/profile targeting for AI coding tools, model releases, new tools, and trend buckets — essential to keep the scope high-signal
- [ ] Deduplication/clustering across overlapping coverage — essential to solve the actual user pain
- [ ] Relevance ranking that outputs a small daily shortlist — essential to avoid recreating the firehose
- [ ] Discord digest with citations and short "why it matters" notes — essential because Discord is the intended consumption surface
- [ ] Basic feedback controls (mute source/topic, thumbs up/down) — essential so the system improves instead of staying noisy
- [ ] Visible run success/failure summary in chat — essential for trust and debugging

### Add After Validation (v1.x)

- [ ] Novelty / first-seen scoring — add when basic digest quality is stable and timeliness becomes the next bottleneck
- [ ] Personalized taste memory — add once enough feedback exists to justify durable preference learning
- [ ] Trend rollups across days — add once daily items are reliable enough to support higher-level pattern detection
- [ ] One-click actions to save an item as a resource or post idea — add when adjacent workflows start being exercised

### Future Consideration (v2+)

- [ ] Structured intel workspace for companies, tools, and models — defer until the digest pipeline is trusted and reusable
- [ ] Competitor / prospect / partner monitoring briefs — valuable later, but needs stronger entity memory and workflow templates
- [ ] Post-idea generation workflow from accumulated intel — defer until the user has enough saved signals and preferences
- [ ] Selective urgent alerts for exceptional events — defer until the system can distinguish genuinely urgent events from hype

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Multi-source collection | HIGH | MEDIUM | P1 |
| Topic/profile targeting | HIGH | LOW | P1 |
| Deduplication + clustering | HIGH | HIGH | P1 |
| Relevance ranking / digest selection | HIGH | HIGH | P1 |
| Discord digest delivery | HIGH | MEDIUM | P1 |
| Explainability / citations | HIGH | MEDIUM | P1 |
| Feedback and suppression controls | HIGH | MEDIUM | P1 |
| Run visibility / failure visibility | MEDIUM | MEDIUM | P1 |
| "Why this matters" synthesis | HIGH | MEDIUM | P2 |
| Novelty / first-seen scoring | HIGH | HIGH | P2 |
| Personalized taste memory | HIGH | HIGH | P2 |
| Trend rollups across days | MEDIUM | HIGH | P3 |
| Structured intel objects | HIGH | HIGH | P3 |
| One-click downstream actions | MEDIUM | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have after core validation
- P3: Valuable, but better after the main workflow proves itself

## Roadmap Implications

- **Phase 1 should focus on signal quality, not surface breadth.** The hardest product problem is not delivery; it is deciding what is worth saying once per day.
- **Deduplication, ranking, and feedback belong in the first serious build phase.** Without them, the digest will feel like a prettier version of the current noise sources.
- **Structured intel objects should be designed early, even if lightly implemented later.** They are the cleanest bridge from news monitoring into resource discovery, post ideas, and research workflows.
- **Visible workflow events are part of the product experience, not just architecture plumbing.** For a personal agent, trust comes from seeing what ran, what was skipped, and why.

## Sources

- Internal project context: `C:\Users\galzi\src\personal-agent-hub\.planning\PROJECT.md` — HIGH
- Internal architecture note: `C:\Users\galzi\src\personal-agent-hub\.planning\notes\visible-routing-architecture.md` — HIGH
- Internal architecture note: `C:\Users\galzi\src\personal-agent-hub\.planning\notes\layered-memory-model.md` — HIGH
- Feedly docs, "Refining Feedly AI Feeds" (updated 2025-07-21): https://docs.feedly.com/article/549-refining-feedly-ai-feeds — MEDIUM
- Feedly docs, "Duplicate Articles" (updated 2023-02-23): https://docs.feedly.com/article/202-duplicate-articles — MEDIUM
- Feedly docs, "Mute Filters" category: https://docs.feedly.com/category/706-mute-filters — MEDIUM
- Feedly docs, "Deduplication" category: https://docs.feedly.com/category/708-deduplication — MEDIUM
- Feedly product page, Market Intelligence: https://feedly.com/market-intelligence — MEDIUM
- Inoreader features page: https://www.inoreader.com/features — MEDIUM

---
*Feature research for: Personal Agent Hub*
*Focus: personal AI-intel/news workflow first, with explicit future-workflow unlocks*
