# Roadmap Risk Review: Personal Agent Hub

**Document reviewed:** `.planning/ROADMAP.md` (state as of 2026-04-27)  
**Review date:** 2026-04-27  
**Reviewer:** Claude Code (plan-risk-review skill)  
**Current position:** Phase 2 complete. Phases 3–9 planned.

---

## 1. Plan Summary

**Purpose in one sentence:** Build a fully automated, daily Discord digest that ingests AI news from multiple RSS feeds, ranks items by relevance, deduplicates across days, and delivers reliably on a fixed schedule - running on MicroClaw today and migrating to Nanoclaw as a final step.

**Key components and actors:**

| Component | Role |
|-----------|------|
| MicroClaw | Scheduling + hosting platform (phases 3–8) |
| Python pipeline (`agent_hub`) | Ingestion, filtering, ranking, formatting |
| OpenRouter | LLM API for ranking + "why it matters" generation |
| RSS feeds (9 sources) | Raw news intake |
| SQLite | Run state, raw items, seen URLs |
| Discord | Sole delivery channel |
| Nanoclaw | Migration target (Phase 9) |

**The plan's own stated assumptions:**  
- MicroClaw is viable (validated Phase 0, R1 closed)  
- OpenRouter model quality is sufficient (validated Phase 0, R3 closed)  
- RSS watchlist has adequate coverage (Phase 0 R4 pass - but live run contradicted this)

**Theory of success:** Each phase adds one capability (ranking → coverage → dedup → schedule → healing → logs → migration) in sequential order. Each capability builds on a stable prior layer. No phase regresses a prior one.

**What must go right:** The ingestion layer must be reliable before ranking adds value; the ranking layer must be stable before scheduling matters; MicroClaw must remain viable through Phase 8 before migration occurs in Phase 9.

---

## 2. Assumptions & Evidence

### A1 - Phase 3 (Ranking) can proceed before Phase 4 (Source Coverage Fix)

**Type:** Implicit  
**Classification:** Foundational  
**Evidence:** None - this assumption is contradicted by the STATE.md blocker explicitly logged by the author: *"Phase 4 (Source Coverage Fix) must diagnose and fix before Phase 3 ranking is meaningful."*  
**What if wrong:** Phase 3 builds an LLM ranking layer on top of an ingester that silently produces items from a single source (OpenAI Blog). The ranking output will look correct but will be systematically biased. This is worse than no ranking: it creates false confidence in a broken pipeline.  
**Testable?** Yes - this is a secret. The source bias is already observed in the first live run. The fix belongs before ranking is built.

### A2 - OpenRouter will be available reliably at digest time

**Type:** Implicit  
**Classification:** Structural  
**Evidence:** Phase 0 evaluation confirmed quality, not availability. OpenRouter is a third-party routing service; outages are outside the author's control.  
**What if wrong:** At 09:00 AM Israel time, the pipeline calls OpenRouter for ranking and "why it matters" generation. If OpenRouter is down, the digest fails silently (or errors). Phase 7 (Self-Healing) handles missed *scheduled* runs but not API-level failures within a run.  
**Testable?** Partial secret - OpenRouter's SLA and historical uptime can be checked; whether the pipeline has a graceful degradation path is verifiable from code.

### A3 - RSS feeds remain available, parseable, and AI-relevant

**Type:** Implicit  
**Classification:** Structural  
**Evidence:** Phase 0 backtested against one week of historical AI news. No ongoing monitoring for feed health is planned in any phase.  
**What if wrong:** A feed drops, changes format, or shifts editorial focus (e.g., a blog that covered AI pivots to a different topic). The pipeline continues to "succeed" with fewer items, and the digest silently degrades. The user may not notice for days.  
**Testable?** Secret - per-source item counts already noted as a Phase 4 success criterion. That logging will serve as detection.

### A4 - MicroClaw remains viable through Phase 8 (seven more phases)

**Type:** Explicit but under-examined  
**Classification:** Structural  
**Evidence:** Phase 0 validated MicroClaw for current capability. Phase 9 plans migration away from it. No evaluation of whether MicroClaw has known issues, deprecation risk, or capability gaps for phases 3–8 features (e.g., startup hooks for Phase 7).  
**What if wrong:** If MicroClaw cannot support self-healing startup hooks (Phase 7) or introduces instability, the author is committed to a platform they are planning to abandon anyway - and must either hack around limitations or accelerate Phase 9 out of sequence.  
**Testable?** Secret - check MicroClaw docs for startup hook support and maintenance trajectory before Phase 7.

### A5 - OpenSearch or Elasticsearch runs acceptably on Windows for Phase 8

**Type:** Implicit  
**Classification:** Structural  
**Evidence:** None. Phase 8 explicitly defers evaluation ("Evaluate OpenSearch vs Elasticsearch for Windows-friendly local dev setup").  
**What if wrong:** Windows-hosted Elasticsearch has significant known operational friction: WSL2 memory configuration, JVM heap tuning, Windows path handling. A personal project's local logging infrastructure should not require tuning a JVM cluster.  
**Testable?** Secret - can be validated in a half-day spike before committing Phase 8 to this approach.

### A6 - Nanoclaw is production-ready and functionally equivalent to MicroClaw for this use case

**Type:** Implicit  
**Classification:** Foundational (for Phase 9)  
**Evidence:** The roadmap cites a GitHub URL. No evaluation of Nanoclaw's maturity, API stability, Windows support, Discord posting, or scheduler capability has occurred.  
**What if wrong:** Phase 9 migration discovers that Nanoclaw lacks a feature MicroClaw provided (e.g., the inbound @-mention routing noted in STATE.md as D-23). The migration stalls or requires significant workarounds after 7 phases of pipeline work.  
**Testable?** Secret - a brief capability spike (analogous to Phase 0 Plan 00-01 for MicroClaw) should precede Phase 9 planning.

### A7 - LLM ranking produces consistent, useful relevance scores

**Type:** Implicit  
**Classification:** Structural  
**Evidence:** Phase 0 evaluated OpenRouter quality on 10–20 summarization tasks. Ranking - assigning a relative relevance ordering to a diverse daily item set - is a different and harder task. No rubric for "relevance" is defined. LLM outputs are nondeterministic.  
**What if wrong:** The ranked digest looks plausible but items near the top on Tuesday look similar to items that scored low on Monday. The user has no way to detect quality drift without a ground-truth benchmark. The digest silently becomes low-signal noise.  
**Testable?** Partially - a small evaluation (5–10 digest days, manual assessment) can detect whether ranking is consistent. A fixed relevance rubric in the prompt reduces nondeterminism.

### A8 - SQLite is sufficient for seen_urls accumulation without maintenance

**Type:** Implicit  
**Classification:** Peripheral now, structural later  
**Evidence:** No capacity planning mentioned for Phase 5. An AI news digest accumulating seen URLs at ~10 items/day reaches ~3,650 rows/year - well within SQLite's range. Not a near-term concern, but no vacuum or archival strategy exists.  
**What if wrong:** Not a risk at current scale. Flag for if digest volume increases significantly.

---

## 3. Ipcha Mistabra - Devil's Advocacy

### 3a. The Inversion Test

**Plan assertion:** "Phases execute in numeric order: 0 → 1 → ... → 9"  
**Inversion:** The phase ordering is wrong in at least one critical place, and following it strictly will waste a development cycle.

Phase 3 (Ranked Digest) is sequenced before Phase 4 (Source Coverage Fix). The ranking machinery is expensive to build (LLM prompt engineering, scoring pipeline, "why it matters" generation). If Phase 4 discovers that the source bias requires changes to the ingester or filter - which is likely, since only one of nine sources contributed items in the first live run - Phase 3's ranking logic may need to be retested or adjusted against a corrected dataset. The plan's own STATE.md says "Phase 4 must diagnose and fix before Phase 3 ranking is meaningful." That is not a caveat; it is a sequencing requirement. The roadmap and the state file contradict each other.

**Plan assertion:** "OpenSearch / Elasticsearch for persistent searchable logs"  
**Inversion:** A full-text search cluster is the wrong infrastructure for a personal daily digest pipeline, and Phase 8 as written is overengineered to the point where it will likely be skipped or abandoned.

OpenSearch and Elasticsearch are designed for multi-node production logging at scale. For a single user running a daily pipeline that produces 10–50 log events per run, the operational overhead (cluster management, index lifecycle, disk usage monitoring, JVM tuning) exceeds the value delivered. Structured JSON logs written to rotating files plus `jq` or `sqlite` queries would satisfy "searchable by run ID, timestamp, and log level" at a fraction of the complexity. The plan frames this as "complementing" SQLite rather than replacing it - which means running two persistence layers for log data that SQLite could handle alone.

**Plan assertion:** "Migrate to Nanoclaw as Phase 9 - depends on all prior phases stable"  
**Inversion:** Deferring the migration evaluation to Phase 9 maximizes the risk of the migration, not minimizes it.

If Nanoclaw turns out to have capability gaps (no startup hooks, different Discord API surface, no Windows support), discovering this after 9 phases of MicroClaw-specific work means the entire pipeline is entangled with MicroClaw idioms. A migration spike *now* (analogous to Phase 0 Plan 00-01) would surface those gaps when the cost of addressing them is low. Phase 9 as written is "migrate after you're fully committed to the platform you're leaving."

---

### 3b. The Little Boy from Copenhagen

**From an ops perspective** (the person who will debug a failed digest at 9:15 AM):  
The pipeline has no alerting. A failed run writes to the SQLite `runs` table - but who reads the `runs` table before checking Discord? Phase 2 delivers a "partial: posted X/Y" message on mid-stream failure, but a complete OpenRouter failure before any posting produces... nothing. No Discord message, no notification, no push alert. The user discovers the missed digest by not seeing it. Phases 7 and 8 address this eventually, but the window between Phase 2 and Phase 7 is four development phases with no observability into silent failures.

**From the perspective of a future self six months from now:**  
The roadmap has no deprecation or cleanup plan for any phase. Phase 9 retires MicroClaw config - but who retires the Phase 1 pipeline orchestration that was designed around MicroClaw's call conventions? Nanoclaw likely has a different entrypoint pattern. The code written in phases 1–8 may accumulate MicroClaw-isms that are invisible until Phase 9 surfaces them as migration friction.

**From a budget perspective:**  
OpenRouter costs for daily ranking are untracked. At 10 items/day ranked + "why it matters" generated per item, with GPT-4-class models, costs could range from $0.01 to $0.10/day - negligible, but unmonitored. If the digest grows (more sources, longer items, more expensive models in Phase 3), cost can drift upward silently. No phase installs a cost checkpoint.

---

### 3c. Failure of Imagination

**The silent-success failure:** Every phase marks success by "tests green" and a Discord post. But what if the Discord post goes out with zero items because all items were filtered? The `run_digest` reports `success`, the `runs` table shows `success`, and the user sees a header message with no items. No phase defines a minimum-item threshold that would trigger a warning or investigation signal.

**The MicroClaw process death scenario:** MicroClaw is presumably a persistent process or service. If it crashes between Phase 2 (today) and Phase 7 (self-healing), there is no mechanism to detect the crash or restart the process. Phase 7 handles "machine was off at scheduled time" but not "MicroClaw process died at 07:30 and the schedule never fired." This is a distinct failure mode.

**The Phase 4 diagnosis could be larger than expected:** Phase 4 is allocated one plan ("Audit ingester/filter for source bias, add per-source logging, fix coverage gaps"). But if the root cause is that eight of nine RSS feeds are returning items with publication dates in the past (thus filtered out by a recency filter), or that the relevance filter has an overly narrow keyword set, the fix could touch multiple modules and require re-running Phase 2 tests. One plan may be optimistic.

**The Phase 9 migration could find that Nanoclaw is unmaintained:** The GitHub URL in the roadmap points to `qwibitai/nanoclaw`. If this repository has had no commits in 6 months by Phase 9, the author is migrating to an unmaintained platform. The roadmap does not include a "Nanoclaw is active and maintained" success criterion in Phase 9 Plan 09-01.

---

## 4. Risk Register

### Priority: Critical

| Field | Value |
|-------|-------|
| **Risk ID** | R1 |
| **Category** | Technical / Schedule |
| **Description** | Phase 3 (Ranked Digest) is sequenced before Phase 4 (Source Coverage Fix), but ranking on a broken ingester that produces items from only one of nine sources delivers biased output and wastes the ranking development effort |
| **Trigger** | Phase 3 begins while source coverage bug from the first live run remains unresolved |
| **Probability** | High - this is the current planned sequence |
| **Severity** | High - Phase 3 ranking work may need partial rework after Phase 4 fixes ingestion |
| **Priority** | Critical |
| **Detection** | Per-source item counts in Phase 4 logs; manually checking ranked digest source diversity |
| **Mitigation** | Swap Phase 3 and Phase 4 in execution order. Fix source coverage before building ranking. |
| **Contingency** | If Phase 3 is built first, explicitly re-run Phase 3 evaluation tests after Phase 4 ships |
| **Assumption link** | A1 |

---

### Priority: High

| Field | Value |
|-------|-------|
| **Risk ID** | R2 |
| **Category** | Operational |
| **Description** | OpenRouter outage during the daily digest window produces a silent failure - no Discord post, no alert, no catch-up mechanism until Phase 7 ships |
| **Trigger** | OpenRouter API returns 5xx or times out during Phase 3+ ranking call |
| **Probability** | Medium - third-party APIs have unplanned outages |
| **Severity** | High - the user discovers missed digests by not seeing them |
| **Priority** | High |
| **Detection** | Runs table status; absence of morning Discord post |
| **Mitigation** | Add graceful degradation: if ranking call fails, fall back to thin digest (unranked) and post with a warning header. This is a straightforward change in `pipeline.py`. |
| **Contingency** | Phase 7 self-healing catches missed days; does not address within-run API failures |
| **Assumption link** | A2 |

| Field | Value |
|-------|-------|
| **Risk ID** | R3 |
| **Category** | Technical / Strategic |
| **Description** | Nanoclaw capability gaps are undiscovered until Phase 9, after all prior phases have been written against MicroClaw's API surface |
| **Trigger** | Phase 9 evaluation finds Nanoclaw lacks startup hooks (needed by Phase 7), inbound routing (D-23 in STATE.md), or Windows support |
| **Probability** | Medium - Nanoclaw is a GitHub project with no evaluated maturity |
| **Severity** | High - could force significant rework of phases 6–8 or block migration entirely |
| **Priority** | High |
| **Detection** | Phase 9 Plan 09-01 evaluation |
| **Mitigation** | Run a brief Nanoclaw capability spike now (before Phase 3), analogous to Phase 0 Plan 00-01 for MicroClaw. Surface gaps while cost of addressing them is low. |
| **Contingency** | Remain on MicroClaw; accept Phase 9 as optional if Nanoclaw is not viable |
| **Assumption link** | A6 |

| Field | Value |
|-------|-------|
| **Risk ID** | R4 |
| **Category** | Technical |
| **Description** | OpenSearch / Elasticsearch on Windows (Phase 8) is significantly harder to operate than the roadmap implies; Phase 8 may stall or be abandoned |
| **Trigger** | Phase 8 attempt to stand up local search cluster encounters JVM/WSL2/Windows path issues |
| **Probability** | High - Windows-hosted ES is a known pain point |
| **Severity** | Medium - Phase 8 delays; phases 3–7 are unaffected |
| **Priority** | High |
| **Detection** | Phase 8 spike attempt |
| **Mitigation** | Before committing to ES/OpenSearch, run a half-day spike. If friction is high, evaluate alternatives: structured JSON logs to files + `jq` queries, DuckDB, or a lightweight SQLite log table. |
| **Contingency** | Descope Phase 8 to "structured JSON logs to rotating files"; defer ES until a non-local environment exists |
| **Assumption link** | A5 |

---

### Priority: Medium

| Field | Value |
|-------|-------|
| **Risk ID** | R5 |
| **Category** | Quality |
| **Description** | LLM ranking is nondeterministic with no defined relevance rubric; quality drift goes undetected over time |
| **Trigger** | Prompt returns different orderings for equivalent content on different days; model updates on OpenRouter change behavior |
| **Probability** | Medium - LLMs have inherent output variance; OpenRouter model versions change |
| **Severity** | Medium - digest is usable but reliability of "why it matters" annotations degrades |
| **Priority** | Medium |
| **Detection** | Manual spot-check of 5 consecutive digests after Phase 3 ships |
| **Mitigation** | Define a written relevance rubric in the ranking prompt (e.g., "score 1–5 based on: novelty, impact on LLM practitioners, recency"). Rubric anchors LLM output across runs. |
| **Contingency** | Add a model-version pin to `config/models.yaml` to prevent silent model updates |
| **Assumption link** | A7 |

| Field | Value |
|-------|-------|
| **Risk ID** | R6 |
| **Category** | Operational |
| **Description** | RSS feed health degrades silently - feeds disappear, change format, or shift editorial focus - and the digest shrinks without any warning |
| **Trigger** | A feed returns HTTP 404, malformed XML, or consistently irrelevant items |
| **Probability** | Medium - RSS feeds have unpredictable maintenance |
| **Severity** | Medium - fewer items, potentially single-source coverage recurrence |
| **Priority** | Medium |
| **Detection** | Per-source item counts (planned in Phase 4); HTTP status logging in ingester |
| **Mitigation** | Phase 4 per-source logging addresses detection. Add a feed-health check that warns (not errors) if a source contributes zero items for N consecutive days. |
| **Contingency** | Maintain a list of backup feeds to swap in when primary feeds degrade |
| **Assumption link** | A3 |

| Field | Value |
|-------|-------|
| **Risk ID** | R7 |
| **Category** | Operational |
| **Description** | MicroClaw process crash between Phase 2 and Phase 7 produces days of missed digests with no detection mechanism |
| **Trigger** | MicroClaw process exits unexpectedly (crash, OOM, Windows update reboot outside scheduled window) |
| **Probability** | Low-Medium - Windows process stability varies |
| **Severity** | Medium - silent missed digests, no user notification |
| **Priority** | Medium |
| **Detection** | Absence of Discord posts; manual `runs` table check |
| **Mitigation** | Register MicroClaw as a Windows Service or add a watchdog. Alternatively, pull Phase 7 (self-healing) earlier in the execution order - it addresses the symptom even if not the root cause. |
| **Contingency** | Manual pipeline invocation; Phase 7 catch-up fires on next restart |
| **Assumption link** | A4 |

| Field | Value |
|-------|-------|
| **Risk ID** | R8 |
| **Category** | Quality |
| **Description** | Zero-item digest posts as "success" - header message appears, no items follow, user receives no signal that something went wrong |
| **Trigger** | All ingested items filtered by relevance filter, or no new items across all sources on a given day |
| **Probability** | Low-Medium - depends on relevance filter aggressiveness |
| **Severity** | Medium - user gets a false green signal from the pipeline |
| **Priority** | Medium |
| **Detection** | Manual Discord check; item count in `runs` table |
| **Mitigation** | Add minimum-item threshold check in `pipeline.py`: if `len(items) == 0`, post a distinct "no qualifying items today" message rather than a normal digest. Track threshold separately from success/failure. |
| **Contingency** | Tune relevance filter sensitivity when zero-item runs recur |
| **Assumption link** | A3 |

---

### Priority: Low

| Field | Value |
|-------|-------|
| **Risk ID** | R9 |
| **Category** | Budgetary |
| **Description** | OpenRouter API costs are unmonitored; cost drift goes undetected as digest volume grows |
| **Trigger** | More items per day, more expensive models selected in Phase 3, or multiple daily runs |
| **Probability** | Low - current item volumes are small |
| **Severity** | Low - this is a personal project with small daily call volumes |
| **Priority** | Low |
| **Detection** | OpenRouter dashboard |
| **Mitigation** | Log estimated token usage per run; set an OpenRouter spend alert if the service supports it |
| **Contingency** | Switch to cheaper models or reduce "why it matters" call frequency |
| **Assumption link** | A7 |

---

## 5. Verdict & Recommendations

### Overall Risk Level: **Moderate**

The foundation (phases 0–2) is solid and the execution has been disciplined. The risks are concentrated in two areas: **phase ordering** (one concrete, already-known mistake) and **deferred validation** (Nanoclaw and OpenSearch evaluated too late). Neither is fatal, but the phase ordering issue will cause waste if not corrected.

---

### Top 3 Risks Requiring Immediate Attention

**1. R1 - Swap Phase 3 and Phase 4 (Critical)**  
The roadmap sequences ranking before source coverage fix. This is wrong and the author already knows it - STATE.md says so explicitly. The fix is zero-code: reorder the phases. Phase 4 (Source Coverage Fix) should ship before Phase 3 (Ranked Digest).

**2. R3 - Run a Nanoclaw capability spike before Phase 3 (High)**  
Committing 7 phases to MicroClaw while planning to abandon it in Phase 9 is only acceptable if Nanoclaw is validated as a capable migration target. A one-plan spike (analogous to Phase 0 Plan 00-01) surfaces blockers while they are cheap to address. If Nanoclaw is not viable, Phase 9 can be dropped; if Nanoclaw is viable, Phase 9 planning is de-risked.

**3. R2 - Add graceful degradation for OpenRouter failures before Phase 3 ships (High)**  
The ranking layer introduces a new single-point-of-failure on a third-party API. Before Phase 3 ships, add a fallback: if the ranking call fails, post an unranked thin digest with a warning. This is a small code change in `pipeline.py` with high defensive value.

---

### Recommended Actions

1. **Reorder phases 3 and 4.** Execute Phase 4 (Source Coverage Fix) first, then Phase 3 (Ranked Digest). Update ROADMAP.md and STATE.md accordingly.

2. **Add a Nanoclaw spike as Phase 3.5 (or an unnumbered quick task)** before committing to MicroClaw-specific features in phases 6–7. Accept or reject Nanoclaw based on evidence, not a deferred evaluation.

3. **Add OpenRouter fallback before Phase 3 ships.** In `pipeline.py`, catch the OpenRouter ranking failure and post an unranked digest with a header note like `[unranked - ranking service unavailable]`. One defensive branch; high reliability value.

4. **Define a relevance rubric before implementing Phase 3 ranking.** Write down what makes an AI news item "relevant" (novelty, practitioner impact, recency weight) as a prompt preamble. This reduces nondeterminism and makes quality evaluation tractable.

5. **Run a half-day Phase 8 spike before planning Phase 8 in detail.** Confirm that OpenSearch or Elasticsearch can be stood up on Windows with acceptable friction. If not, descope to structured JSON file logs. Do not plan two Phase 8 plans against an unvalidated infrastructure assumption.

6. **Add a zero-item warning path to the pipeline.** Before Phase 3 ships, distinguish between "ran successfully, 0 qualifying items" and "ran successfully, N items posted." Post a distinct Discord message for the zero-item case.

---

### Open Questions

- Does MicroClaw support startup hooks (needed by Phase 7's self-healing design)? This is a secret - check the MicroClaw docs or test it before Phase 7 planning begins.
- What is Nanoclaw's current maintenance status? How many open issues? Last commit date? This is a secret - readable from the GitHub repository now.
- What is the actual root cause of the single-source (OpenAI Blog only) live run? Is it the relevance filter, publication date filtering, feed fetch failures, or encoding issues? This is a secret - answerable by Phase 4 investigation.
- Will OpenRouter model versions be pinned or float? If they float, ranking quality can change without notice. This is a secret - check OpenRouter's model versioning API.
- Is the user's definition of "relevance" stable enough for a fixed prompt rubric, or does it evolve weekly? This is a mystery - needs periodic rubric review.

---

### What the Plan Does Well

The roadmap is honest about its own gaps. Phase 4 explicitly acknowledges the source coverage bug from the first live run rather than hiding it. The decision to ship a thin digest (Phase 2) before ranking (Phase 3) was sound - early delivery validates the end-to-end path before adding complexity. Phase 7 (self-healing) and Phase 5 (URL deduplication) address real reliability gaps that simpler roadmaps would ignore. The Phase 0 spike discipline (validate before building) is exactly right and should be applied to Nanoclaw before Phase 9 planning begins.

The overall risk posture is correctable. No risks identified here are architectural dead ends. They are sequencing decisions and deferred evaluations that can be addressed with small plan adjustments before Phase 3 work begins.

---

*Generated by plan-risk-review skill. This document is a point-in-time assessment and should be revisited after Phase 4 completes.*
