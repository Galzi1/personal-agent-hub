# Domain Pitfalls

**Domain:** personal AI-agent news/intelligence workflow for AI tooling and model updates  
**Researched:** 2026-04-11  
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Treating "more sources" as better coverage

**What goes wrong:**  
The system ingests many feeds, communities, and social posts, but output quality gets worse. The digest becomes repetitive, contradictory, and noisy because source count grows faster than source quality control.

**Why it happens:**  
AI-news builders often optimize for collection breadth first. In this domain, most sources are downstream amplifiers of the same small set of original announcements, demos, and rumor threads.

**Consequences:**  
- Duplicate items dominate the digest
- Low-signal "AI influencer echo" crowds out actual product changes
- User stops trusting the feed as a high-signal source

**Prevention:**  
- Define source classes early: primary, secondary, commentary, rumor
- Weight primary sources highest: official blogs, release notes, model cards, product changelogs, vendor X/Discord announcements
- Cap low-trust/community-only sources until they prove value
- Track per-source usefulness: unique hits, false positives, repeated duplicates, late coverage rate
- Build a denylist and "watch but do not publish" tier

**Warning signs:**  
- Many digest items cite each other instead of an original source
- Same story appears 3-5 times with slightly different wording
- "Interesting" items are mostly social reactions, not substantive changes
- Source count rises but unique valuable items do not

**Phase to address:**  
Phase 1 - Source acquisition and provenance rules

---

### Pitfall 2: Weak deduplication that only matches exact URLs or titles

**What goes wrong:**  
The system treats the same event as separate items because different outlets rewrite titles, deep-link different pages, or add commentary around the same underlying announcement.

**Why it happens:**  
Teams implement basic URL or title dedupe and assume the problem is solved. AI news spreads via paraphrase, screenshots, quote-posts, and aggregator rewrites.

**Consequences:**  
- Digest feels spammy
- Ranking is distorted because repeated coverage looks like multiple independent events
- Later memory layers store duplicates as if they were separate facts

**Prevention:**  
- Deduplicate at the "story/event" level, not the document level
- Extract canonical event entities: vendor, product, version/model, action, timestamp
- Cluster similar items within a freshness window before ranking
- Preserve one canonical record plus supporting references
- Keep confidence on cluster merges visible so mis-merges can be reviewed

**Warning signs:**  
- User says "you already told me this"
- Multiple top-ranked items refer to one launch
- Memory contains near-identical facts with slightly different wording
- Ranking spikes correlate with number of reposts, not significance

**Phase to address:**  
Phase 1 - Canonicalization and dedupe pipeline

---

### Pitfall 3: Ranking popularity instead of user relevance

**What goes wrong:**  
The digest overweights what is broadly viral instead of what matters to this user: new models, coding-tool updates, useful AI tools, and hot trends with practical leverage.

**Why it happens:**  
Engagement is easier to measure than relevance. Social buzz is mistaken for importance.

**Consequences:**  
- Feed becomes generic "AI Twitter recap"
- Important but quieter updates are missed
- User still has to do manual filtering after reading the digest

**Prevention:**  
- Rank with an explicit scoring model: relevance, novelty, credibility, actionability, freshness, and duplicate-adjusted momentum
- Give dedicated boosts to user priorities: model releases, Claude Code/Cursor changes, new useful tools, real shifts in workflows
- Penalize pure commentary, outrage, and vague speculation
- Require a short "why this matters" field for each surfaced item
- Use feedback loops to calibrate ranking against actual user saves/ignores

**Warning signs:**  
- Digest reads like a trend roundup instead of an intelligence brief
- Quiet but important vendor updates are absent
- User consistently ignores top-ranked "hot takes"
- Ranking changes are hard to explain

**Phase to address:**  
Phase 2 - Relevance scoring and digest composition

---

### Pitfall 4: Optimizing for daily cadence but missing freshness windows

**What goes wrong:**  
A once-daily digest arrives after the user has already heard the news elsewhere, defeating the core value of earlier discovery.

**Why it happens:**  
Teams scope "daily digest" too literally and ignore collection latency, source polling cadence, and event aging.

**Consequences:**  
- Product feels reactive, not useful
- High-value early signals are discovered too late
- The user sees the digest as archival rather than decision-support

**Prevention:**  
- Separate ingestion cadence from delivery cadence
- Poll or collect continuously enough to preserve freshness, even if delivery is daily
- Track event first-seen time, source publication time, and digest send time
- Define freshness thresholds by item type: launch, update, rumor, trend
- Consider "urgent breakout" rules later for major model/tool releases

**Warning signs:**  
- Many digest items are already widely discussed by send time
- Time from original announcement to first ingestion is long or unknown
- No instrumentation for first-seen vs delivered lag
- Digest quality is high but still feels late

**Phase to address:**  
Phase 1 - Freshness-aware ingestion; Phase 2 - digest timing policy

---

### Pitfall 5: Invisible or unexplainable routing

**What goes wrong:**  
Items appear in Discord without clear provenance, why they were selected, or which agent/policy decided. This breaks trust and makes debugging ranking mistakes painful.

**Why it happens:**  
Builders keep orchestration hidden inside agent internals. That is especially tempting early when only one user exists.

**Consequences:**  
- User cannot tell whether an item came from solid sourcing or model guesswork
- Hard to debug missed stories, duplicates, or bad rankings
- Future workflow expansion becomes brittle because the routing logic is opaque

**Prevention:**  
- Make major handoffs visible in chat for this workflow
- Attach provenance and selection rationale to each digest item
- Link digest items to control-panel traces and canonical source records
- Keep hidden model chatter non-authoritative for major workflow transitions
- Add loop-prevention and escalation rules before expanding beyond one workflow

**Warning signs:**  
- Team cannot answer "why did this make the digest?"
- Digest items lack source lineage
- Misses and mistakes require log-diving across multiple components
- Routing logic lives in prompts instead of explicit policy

**Phase to address:**  
Phase 1 - Workflow visibility and trace model

---

### Pitfall 6: Letting the agent summarize before it has verified the event

**What goes wrong:**  
The agent generates a polished summary of an item that is still rumor, misread, or based on weak secondary coverage.

**Why it happens:**  
LLM fluency hides evidence gaps. Summarization is used too early in the pipeline instead of after source verification and canonicalization.

**Consequences:**  
- Hallucinated certainty
- Wrong details get repeated in memory and future digests
- Trust drops sharply after a few visible errors

**Prevention:**  
- Gate summarization on minimum provenance thresholds
- Label rumor/speculation explicitly and downgrade it
- Require evidence slots: original source, supporting source, confidence, unresolved questions
- Use extraction-first, summary-second pipeline design
- Store uncertainty in structured form instead of flattening it into prose

**Warning signs:**  
- Summaries are confident even when source quality is weak
- Contradictions across items are not surfaced
- Rumors and official launches are formatted the same way
- The model fills missing fields instead of marking unknown

**Phase to address:**  
Phase 1 - Evidence model; Phase 2 - summary generation policy

---

### Pitfall 7: Memory pollution from low-signal or unvalidated observations

**What goes wrong:**  
The layered memory system accumulates rumors, one-off preferences, duplicate facts, and stale trend judgments. Future ranking and summarization then inherit bad context.

**Why it happens:**  
Teams treat every interaction log as memory-worthy. In this product, news-like data is especially perishable and noisy.

**Consequences:**  
- Agents become overfit to temporary hype cycles
- Old or wrong judgments influence new decisions
- Shared memory becomes a trash heap instead of a trusted asset

**Prevention:**  
- Use strict promotion rules from transient logs to durable memory
- Keep source-derived event records separate from durable preference memory
- Promote only validated wins, stable preferences, and reusable judgments
- Add TTL/review rules for trend claims and tool evaluations
- Make shared memory stricter than agent-local memory, as already planned

**Warning signs:**  
- Memory grows quickly with little curation
- Old trend narratives keep reappearing
- Shared memory contains duplicates or rumor-like statements
- Agents cite prior internal memory over source evidence

**Phase to address:**  
Phase 2 - Memory write policy and hygiene automation

---

### Pitfall 8: Conflating "interesting" with "actionable"

**What goes wrong:**  
The digest is full of neat demos, speculative startups, and novelty posts that are entertaining but not useful for the user's actual business/personal intelligence goals.

**Why it happens:**  
AI news is unusually hype-heavy. Builders optimize for wow-factor because it feels valuable during demos.

**Consequences:**  
- User attention is consumed without increasing leverage
- The system underdelivers on tool discovery and strategic awareness
- Digest becomes content, not intelligence

**Prevention:**  
- Add an actionability dimension to ranking
- Distinguish "important to know" from "worth trying" from "trend to monitor"
- Require a user-centric takeaway on each item
- Limit novelty/demo slots in the final digest
- Review ignored items to identify entertainment-heavy drift

**Warning signs:**  
- Many items do not imply any decision, awareness change, or follow-up
- Demos outrank real product availability
- User reaction is "interesting" but no saves, clicks, or follow-up actions happen
- Tool recommendations feel random

**Phase to address:**  
Phase 2 - Ranking rubric and digest UX

---

### Pitfall 9: Overbuilding a worker mesh before proving one reliable workflow

**What goes wrong:**  
The team designs a broad multi-agent ecosystem for research, idea generation, prospecting, and more before the daily AI digest is stable.

**Why it happens:**  
Agent systems invite architectural ambition. The platform vision starts to dominate the v1 proof point.

**Consequences:**  
- Core workflow remains unreliable
- Complexity hides signal-quality problems
- Debugging becomes distributed before the team understands the basic loop

**Prevention:**  
- Keep v1 to one visible end-to-end workflow
- Add new workers only after the digest pipeline has measurable quality
- Make routing policy thin and explicit above MicroClaw
- Prefer manual review checkpoints over premature automation breadth

**Warning signs:**  
- New agent roles appear faster than digest quality improves
- Large orchestration discussions happen before source/ranking metrics exist
- Failures are blamed on "the system" instead of a clear stage
- Control panel traces are rich, but output quality is still poor

**Phase to address:**  
Phase 0 / Foundation - scope control and workflow definition

---

### Pitfall 10: No explicit treatment of uncertainty, rumors, and reversals

**What goes wrong:**  
The system publishes early claims as facts, then has no good way to retract, update, or downgrade them when reality changes.

**Why it happens:**  
AI news moves fast, especially around leaks, benchmark claims, shipping timelines, and "coming soon" feature talk.

**Consequences:**  
- False confidence in the digest
- Memory stores superseded facts
- User cannot distinguish confirmed updates from watchlist items

**Prevention:**  
- Define states such as: observed, corroborated, confirmed, disputed, superseded
- Let canonical stories evolve as new evidence arrives
- Include update/retraction behavior in the pipeline
- Show confidence and source class in Discord output
- Avoid durable memory writes for unresolved claims

**Warning signs:**  
- Old incorrect claims remain uncorrected in later digests
- Same topic reappears without acknowledging prior uncertainty
- There is no schema for confidence or status transitions
- "Rumor" and "release" share the same presentation

**Phase to address:**  
Phase 1 - Story lifecycle model; Phase 2 - output formatting

---

### Pitfall 11: Discord delivery that is readable in demos but bad in daily use

**What goes wrong:**  
The digest is too long, too dense, badly chunked, or impossible to scan on mobile. Important items are buried.

**Why it happens:**  
Builders optimize for rich payload completeness rather than consumption behavior. Discord is treated like email instead of a chat surface.

**Consequences:**  
- User skims or ignores the digest
- Signal density is lost at the last mile
- Feedback loops weaken because interaction is low

**Prevention:**  
- Design for fast scan: tiers, sections, short bullets, clear "why it matters"
- Keep top items above the fold
- Use consistent formatting and bounded item counts
- Reserve long traces for the control panel, not the message body
- Add lightweight reactions/feedback mechanisms

**Warning signs:**  
- Digest requires scrolling through walls of text
- User reads only the first 1-2 items
- Discord formatting differs across runs
- Debug metadata leaks into user-facing output

**Phase to address:**  
Phase 2 - Delivery UX and feedback loop

---

### Pitfall 12: No measurable quality loop for "high-signal" claims

**What goes wrong:**  
The team says the product is "high-signal" but has no metrics for relevance, duplicates prevented, freshness, misses, or user satisfaction.

**Why it happens:**  
Signal quality feels subjective, so builders rely on intuition. In practice, this makes improvement random.

**Consequences:**  
- Roadmap choices are not evidence-based
- Ranking tuning becomes prompt thrash
- Regressions are noticed only anecdotally

**Prevention:**  
- Track metrics per digest: duplicate-collapse rate, median freshness lag, source diversity, user-marked hits, ignored items, missed major stories
- Create a lightweight review rubric for daily/weekly retrospectives
- Log why each item was included and how it scored
- Use human feedback to update ranking weights and source trust

**Warning signs:**  
- Team cannot define what a "good digest" measuredly means
- Changes to prompts/policies are not compared against outcomes
- Complaints are qualitative only
- Missed major stories are discovered by accident

**Phase to address:**  
Phase 1 - instrumentation foundation; Phase 2 - quality tuning loop

## Moderate Pitfalls

### Pitfall 1: Mixing stable references with rapidly expiring trend knowledge
**What goes wrong:** Durable memory stores both evergreen facts and short-lived hype in the same layer.  
**Prevention:** Separate reference memory from trend/event memory; apply TTL and review rules to the latter.  
**Phase to address:** Phase 2 - memory modeling

### Pitfall 2: Failing to preserve the original source once summaries are generated
**What goes wrong:** The team keeps only summaries and loses the exact announcement, post, or changelog that justified them.  
**Prevention:** Keep canonical source pointers and snapshots/metadata for every published item.  
**Phase to address:** Phase 1 - provenance storage

### Pitfall 3: Treating all "AI tools" as one category
**What goes wrong:** Niche toys crowd out serious workflow tools because category boundaries are weak.  
**Prevention:** Classify by user utility: coding tools, model providers, research tools, workflow automation, media tools, etc.  
**Phase to address:** Phase 2 - taxonomy and ranking

## Minor Pitfalls

### Pitfall 1: Over-personalizing too early
**What goes wrong:** Early ranking becomes overly narrow before the system has enough feedback.  
**Prevention:** Start with strong global rules, then add calibrated personalization slowly.  
**Phase to address:** Phase 2 - feedback tuning

### Pitfall 2: Using "hot trend" labels without evidence
**What goes wrong:** The digest labels something a trend because it appears often in a small source bubble.  
**Prevention:** Require cross-source momentum and time-window checks before trend labeling.  
**Phase to address:** Phase 2 - trend detection

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Foundation / v1 scope | Building a broad agent platform before one digest loop works | Freeze v1 around one visible workflow and explicit success metrics |
| Ingestion & sourcing | Too many low-quality sources too early | Start with curated source tiers and provenance tracking |
| Canonicalization | Document-level dedupe only | Implement story/event clustering before ranking |
| Ranking | Popularity proxy replaces relevance | Use explicit scoring dimensions tied to user value |
| Summarization | Fluent output hides weak evidence | Verify first, summarize second; expose confidence |
| Memory | Shared memory becomes polluted | Require promotion rules, TTLs, and consolidation |
| Routing / orchestration | Hidden decisions reduce trust | Keep major handoffs visible in chat and traces |
| Discord delivery | Digest is too dense to consume | Optimize for scanability and short rationale per item |
| Evaluation | "High-signal" remains subjective | Instrument freshness, duplicates, misses, and user feedback |

## Sources

- Internal project direction:
  - `.planning/PROJECT.md`
  - `.planning/notes/layered-memory-model.md`
  - `.planning/notes/visible-routing-architecture.md`
- Confidence note:
  - Findings are primarily based on project docs plus established AI-agent/news-workflow patterns; external verification for domain pitfalls is inherently limited, so overall confidence is MEDIUM.
