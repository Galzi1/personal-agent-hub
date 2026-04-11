# Phase 1: Ingestion Foundation & Run Visibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-11
**Phase:** 1-Ingestion Foundation & Run Visibility
**Areas discussed:** Source watchlist shape, Run visibility in Discord, Run trace details, Schedule and rerun behavior

---

## Source watchlist shape

### Q1. For the first curated intake watchlist, what source mix should Phase 1 target?

| Option | Description | Selected |
|--------|-------------|----------|
| Official product sources + a small curated industry layer | Balances trust with some market awareness | ✓ |
| Official product sources only | Highest confidence, but narrower discovery | |
| Broad mix of official, media, community, and social sources | Widest coverage, most noise | |

**User's choice:** Official product sources + a small curated industry layer
**Notes:** User accepted the recommended balance rather than narrowing to official-only or broadening to community-heavy intake.

### Q2. How tight should the starter watchlist be for Phase 1?

| Option | Description | Selected |
|--------|-------------|----------|
| Small and high-trust — a tight seed list I can expand later | Bias for signal quality and easier tuning | ✓ |
| Medium-sized from day one — enough breadth to feel useful immediately | Broader early coverage with more tuning overhead | |
| As broad as we can manage — coverage matters more than a tight seed list | Maximizes coverage but increases noise risk | |

**User's choice:** Small and high-trust — a tight seed list I can expand later
**Notes:** User preferred a narrow launch boundary over aggressive initial coverage.

### Q3. What should the non-official part of that starter watchlist mostly be?

| Option | Description | Selected |
|--------|-------------|----------|
| High-signal AI news and product trackers, with only a couple trend-watchers | Keeps the non-official layer curated and useful | ✓ |
| Community-first trend sources like X, Reddit, YouTube, and forums | Faster trend pickup, more noise and volatility | |
| Formal press and publications only | Cleaner sourcing, weaker trend sensitivity | |

**User's choice:** High-signal AI news and product trackers, with only a couple trend-watchers
**Notes:** User wanted the non-official layer to stay curated rather than becoming social-first.

### Q4. For sources that do not expose a clean feed or API, what should Phase 1 do?

| Option | Description | Selected |
|--------|-------------|----------|
| Skip them for now unless they become clearly important | Keeps Phase 1 intake reliable and simpler | ✓ |
| Allow a few manual exceptions through a fallback scraper path | Adds some flexibility with limited extra complexity | |
| Use fallback scraping whenever it improves coverage | Maximizes coverage but increases fragility | |

**User's choice:** Skip them for now unless they become clearly important
**Notes:** User accepted the RSS/API-first posture and deferred scraping exceptions.

### Q5. How should the Phase 1 watchlist be managed at launch?

| Option | Description | Selected |
|--------|-------------|----------|
| A simple local config/allowlist edited manually | Smallest surface area and fastest to stabilize | ✓ |
| A small control-panel form for adding/removing sources | More convenient, but adds interface work immediately | |
| Discord commands for managing the watchlist | Chat-native, but expands Phase 1 interaction scope | |

**User's choice:** A simple local config/allowlist edited manually
**Notes:** User preferred a minimal management surface at launch.

### Q6. Should the starter watchlist enforce trust tiers between source types?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — official sources highest, curated trackers next, trend-watchers lowest | Makes source trust explicit from day one | ✓ |
| No — keep one flat allowlist for Phase 1 | Simpler model, weaker trust semantics | |
| Only a light split between official and non-official | Middle ground with less nuance than full tiers | |

**User's choice:** Yes — official sources highest, curated trackers next, trend-watchers lowest
**Notes:** User wanted trust ordering made explicit rather than implied.

### Q7. Which official source types should definitely be in the starter watchlist?

| Option | Description | Selected |
|--------|-------------|----------|
| Product blogs/changelogs and GitHub release feeds | Covers formal product updates and shipped releases | ✓ |
| Blogs/changelogs only | Simpler, but misses release-feed coverage | |
| Blogs/changelogs, GitHub releases, and official social accounts | Broader official coverage with more noise risk | |

**User's choice:** Product blogs/changelogs and GitHub release feeds
**Notes:** User kept official intake focused on structured release-oriented sources.

### Q8. How strict should Phase 1 be about the trend-watcher layer?

| Option | Description | Selected |
|--------|-------------|----------|
| Very strict — only a tiny allowlist of proven high-signal trend-watchers | Keeps trend coverage curated and rare | ✓ |
| Moderately strict — a handful of trend-watchers is fine | Adds breadth with some extra tuning burden | |
| No trend-watchers in Phase 1 at all | Maximizes trust but reduces trend sensitivity | |

**User's choice:** Very strict — only a tiny allowlist of proven high-signal trend-watchers
**Notes:** User wanted a trend layer, but only under tight curation.

---

## Run visibility in Discord

### Q1. How chat-visible should each Phase 1 run be in Discord?

| Option | Description | Selected |
|--------|-------------|----------|
| Show only major milestones — start, key handoffs, and final outcome | Good visibility without chat spam | ✓ |
| Show only the final outcome unless the run fails | Minimal noise, weaker transparency | |
| Show detailed step-by-step progress in chat | Maximum transparency, highest noise | |

**User's choice:** Show only major milestones — start, key handoffs, and final outcome
**Notes:** User wanted visibility, but only at milestone level.

### Q2. Where should those Phase 1 run-status messages appear in Discord?

| Option | Description | Selected |
|--------|-------------|----------|
| In the same Discord surface as the digest, but kept compact | One place to look, but mixes delivery and operations | |
| Dedicated shared agent-status side channel | Keeps the digest channel clean while creating a reusable ops surface | ✓ |
| In direct messages only | Private, but weak as a shared operational surface | |

**User's choice:** Dedicated shared agent-status side channel; keep the digest channel clear and focused
**Notes:** User explicitly said the side channel should later serve all agents, while the digest channel stays focused on the digest itself.

### Q3. When a run succeeds and does produce digest-worthy items, what should the status side channel show?

| Option | Description | Selected |
|--------|-------------|----------|
| A concise success summary with key counts and a link back to the detailed trace | Visible enough for ops, with fast drill-down | ✓ |
| A concise success summary with key counts only | Less navigation help to deeper traces | |
| Just a simple completed message | Lowest noise, weak operational value | |

**User's choice:** A concise success summary with key counts and a link back to the detailed trace
**Notes:** User wanted success posts to be compact but still traceable.

### Q4. What should the status side channel do when a run fails or when it produces no qualifying items?

| Option | Description | Selected |
|--------|-------------|----------|
| Post explicit messages for both cases, each with a short reason and a trace link | Makes all outcomes visible and diagnosable | ✓ |
| Post failures explicitly, but keep no-qualifying-item runs silent | Reduces noise, but hides one valid outcome class | |
| Post failures explicitly, and show no-qualifying-item runs only in the control panel | Keeps chat quieter, weaker user awareness | |

**User's choice:** Post explicit messages for both cases, each with a short reason and a trace link
**Notes:** User wanted "no qualifying items" treated as a visible outcome, not a silent absence.

### Q5. Which milestones are important enough to narrate in the Phase 1 status side channel?

| Option | Description | Selected |
|--------|-------------|----------|
| Run start, ingestion complete, and final outcome only | Keeps the milestone set compact and meaningful | ✓ |
| Only run start and final outcome | Even leaner, but hides one important mid-run checkpoint | |
| Include additional internal milestones like normalization, ranking, and composition | Richer status, but higher noise and more implementation overhead | |

**User's choice:** Run start, ingestion complete, and final outcome only
**Notes:** User drew the milestone boundary at a simple three-event sequence.

---

## Run trace details

### Q1. How should each visible Phase 1 run be labeled in the status side channel?

| Option | Description | Selected |
|--------|-------------|----------|
| A human-readable run label with date/time plus a short run ID | Easy to scan in chat while remaining traceable | ✓ |
| Date/time only | Simpler, but weaker when multiple runs happen close together | |
| A raw UUID or internal run ID only | Precise, but poor readability in chat | |

**User's choice:** A human-readable run label with date/time plus a short run ID
**Notes:** User preferred labels that are both operationally useful and chat-friendly.

### Q2. Where should the trace link from a status message land?

| Option | Description | Selected |
|--------|-------------|----------|
| A dedicated control-panel run detail view for that exact run | More curated first stop | |
| A raw event/log view for that exact run | Direct forensic access with minimal mediation | ✓ |
| A lightweight summary page with no deeper log drill-down | Clean first impression, weaker debugging depth | |

**User's choice:** A raw event/log view for that exact run
**Notes:** User chose direct access to the exact run log rather than a polished summary wrapper.

### Q3. What should that exact run event/log view look like by default?

| Option | Description | Selected |
|--------|-------------|----------|
| An append-only event timeline with timestamps, event type, and outcome markers | Preserves sequence and makes outcomes easy to audit | ✓ |
| A compact step/status table only | Cleaner, but less forensic detail | |
| Full verbose logs shown by default | Maximum detail, but hard to scan | |

**User's choice:** An append-only event timeline with timestamps, event type, and outcome markers
**Notes:** User preferred a forensic timeline over a minimal snapshot or noisy raw dump.

### Q4. If the same day gets retried or manually rerun, how should Phase 1 preserve traceability?

| Option | Description | Selected |
|--------|-------------|----------|
| Every retry/rerun gets its own run label and short ID, with links between related runs | Preserves history without ambiguity | ✓ |
| Reuse one day-level run identity and update it in place | Simpler surface, weaker auditability | |
| Show only the latest attempt unless someone opens the deeper logs | Keeps the main view cleaner, but hides history | |

**User's choice:** Every retry/rerun gets its own run label and short ID, with links between related runs
**Notes:** User wanted retries and manual reruns to stay individually visible and linked.

---

## Schedule and rerun behavior

### Q1. What should the Phase 1 digest cadence be?

| Option | Description | Selected |
|--------|-------------|----------|
| Run every day | Matches the daily digest product promise | ✓ |
| Run on weekdays only | Reduces load, but breaks daily expectation | |
| Use a custom weekly cadence | More tailored, but less predictable | |

**User's choice:** Run every day
**Notes:** User kept the cadence aligned with the daily-digest framing.

### Q2. What local start time should the scheduled Phase 1 run target?

| Option | Description | Selected |
|--------|-------------|----------|
| 07:00 local | Earlier delivery window | |
| **Custom: 08:00 local** | User-corrected preferred morning slot | ✓ |
| 09:00 local | Slightly later morning delivery | |
| 12:00 local | Midday delivery | |

**User's choice:** 08:00 local
**Notes:** User first selected 09:00 local, then explicitly corrected it to 08:00 local before the next question.

### Q3. Should Phase 1 allow manual on-demand reruns in addition to the scheduled daily run?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — manual reruns should exist and be clearly labeled as separate runs | Keeps recovery/testing possible without hiding run history | ✓ |
| No — scheduled runs only in Phase 1 | Simpler, but weaker recovery/debugging path | |
| Only allow manual dry-runs that do not count as real runs | Safer surface, but weaker operational utility | |

**User's choice:** Yes — manual reruns should exist and be clearly labeled as separate runs
**Notes:** User wanted manual reruns, but not at the cost of collapsing trace history.

### Q4. If a scheduled run fails, what should Phase 1 do automatically?

| Option | Description | Selected |
|--------|-------------|----------|
| Retry once after a short delay, then surface failure clearly if it still fails | Balances resilience with transparency | ✓ |
| Do not auto-retry; wait for a manual rerun | Simplest behavior, more manual recovery burden | |
| Retry multiple times automatically before surfacing failure | More resilience, but noisier and harder to reason about | |

**User's choice:** Retry once after a short delay, then surface failure clearly if it still fails
**Notes:** User accepted one automatic retry, not repeated retry loops.

---

## the agent's Discretion

- Exact starter source names within the chosen trust tiers and source types
- Exact local config/allowlist file shape and storage location
- Exact short run ID format and human-readable naming convention
- Exact event schema fields and event-timeline presentation details
- Exact delay before the single automatic retry

## Deferred Ideas

- **Rescope v1 around one visible workflow** — reviewed but not folded because the existing roadmap already bakes that idea into the current phase boundary and project direction
