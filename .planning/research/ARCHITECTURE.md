# Architecture Research

**Domain:** personal AI-agent system for research and intelligence workflows  
**Researched:** 2026-04-11  
**Confidence:** MEDIUM

## Recommended Architecture

For this product, v1 should be structured as a **workflow-oriented local monolith** with clear internal boundaries, not as a broad autonomous worker mesh.

That means:

- **One runtime core** on Windows (MicroClaw + Ollama)  
- **One primary orchestrated workflow** for the daily AI-news digest  
- **A small set of bounded specialist components** for intake, deduplication, ranking, composition, and delivery  
- **An append-only audit/event trail** so Discord-visible routing and control-panel traces both come from the same source of truth

This is the right shape because the real v1 problem is not “how do we coordinate many agents,” it is “how do we reliably turn noisy AI-news inputs into one trusted daily digest.”  
So the architecture should optimize first for **signal quality, repeatability, and auditability**.

### System Overview

```text
┌────────────────────────────────────────────────────────────────────┐
│                        User Surfaces                              │
├────────────────────────────────────────────────────────────────────┤
│ Discord delivery + commands     Control panel / run inspection    │
└───────────────┬───────────────────────────────┬────────────────────┘
                │                               │
┌───────────────▼───────────────────────────────▼────────────────────┐
│                 Workflow Coordination Layer                        │
├────────────────────────────────────────────────────────────────────┤
│ Digest scheduler │ Run orchestrator │ Routing/policy narrator     │
└───────────────┬──────────────┬──────────────┬──────────────────────┘
                │              │              │
┌───────────────▼──────────────▼──────────────▼──────────────────────┐
│                    Domain Services / Workers                       │
├────────────────────────────────────────────────────────────────────┤
│ Source intake │ Normalize │ Dedup/cluster │ Rank/filter │ Compose │
│ Memory promotion │ Feedback handler │ Citation builder            │
└───────────────┬──────────────┬──────────────┬──────────────────────┘
                │              │              │
┌───────────────▼──────────────▼──────────────▼──────────────────────┐
│                         Shared Infrastructure                       │
├────────────────────────────────────────────────────────────────────┤
│ Raw item store │ Canonical story store │ Run/event log │ Memory    │
│ Ollama LLM/embeddings │ Files/config │ Metrics/logs              │
└────────────────────────────────────────────────────────────────────┘
```

## Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| Discord adapter | Sends digest, receives replay/feedback commands, shows major handoffs | Run orchestrator, feedback handler |
| Control panel | Forensic view of runs, stories, rankings, memory promotions, retries | Run/event log, stores, orchestrator |
| Digest scheduler | Triggers the daily digest and manual backfills | Run orchestrator |
| Run orchestrator | Owns run state machine and step ordering | All domain services, event log |
| Routing/policy layer | Decides what becomes chat-visible and prevents noisy handoff spam | Orchestrator, Discord adapter, control panel |
| Source intake | Pulls from RSS/APIs/web sources and stores raw items | External sources, raw item store |
| Normalizer | Converts source-specific items into one article/story candidate schema | Raw item store, canonical story store |
| Dedup/cluster service | Collapses repeated coverage into one canonical story | Canonical story store, Ollama embeddings if needed |
| Rank/filter service | Scores relevance for the user and removes low-signal stories | Canonical story store, memory, Ollama |
| Digest composer | Produces the final daily digest with sections, summaries, and links | Ranked stories, Ollama, Discord adapter |
| Feedback handler | Captures “more/less like this,” missed stories, corrections | Discord adapter, memory promotion |
| Memory promotion | Promotes validated preferences/patterns into layered memory | Memory stores, control panel |
| Event/audit log | Append-only record of every run, decision, handoff, and failure | All components |
| Layered memory | Agent-local calibration + small shared project memory | Rank/filter, composer, feedback handler |

## What v1 Should Actually Be

### Recommended v1 shape

**Use one orchestrated pipeline with bounded specialists.**

The core daily run should look like:

1. ingest source items
2. normalize into one schema
3. cluster duplicates into canonical stories
4. score/filter stories for signal
5. compose digest
6. send digest to Discord
7. log all decisions and expose them in the control panel

This is better than starting with “News Agent → Research Agent → Digest Agent → Memory Agent” as peers with broad autonomy.  
For v1, that pattern adds complexity before the product proves its core value.

### Where the current direction is strong

1. **MicroClaw as execution foundation is directionally strong**  
   Good fit for Windows-first, local-first, chat surfaces, scheduled execution, and a built-in control plane.

2. **Visible routing is strong**  
   For a personal system, trust matters more than theatrical autonomy. Showing major handoffs and completions in Discord is useful.

3. **Layered memory is strong**  
   This is the correct correction to the common mistake of dumping every interaction into one shared memory bucket.

### Where the current direction is risky

1. **Too much agent vocabulary too early**  
   If every step becomes a “worker agent,” you can hide deterministic failures behind vague agent behavior.

2. **Deduplication is the actual hard problem, not orchestration**  
   The first architecture must treat canonical-story formation as a first-class subsystem, not a side effect of summarization.

3. **Memory pollution risk is high**  
   If article summaries, temporary rankings, and one-off opinions all get promoted, the system will degrade quickly.

4. **Control-panel inflation risk**  
   The panel should start as an audit/review surface, not a full no-code orchestration studio.

## Recommended Data Flow

### Daily Digest Run

```text
Scheduler trigger
    ↓
Run orchestrator creates run_id
    ↓
Source intake fetches raw items
    ↓
Normalizer maps items to common schema
    ↓
Dedup/cluster groups overlapping coverage into canonical stories
    ↓
Rank/filter scores stories using rules + LLM judgment
    ↓
Digest composer drafts sections and summaries
    ↓
Discord adapter posts digest
    ↓
Event log + control panel capture run outcome
```

### Decision Flow Inside a Run

```text
Raw item
    ↓
Normalization
    ↓
Canonical story candidate
    ↓
Duplicate cluster decision
    ↓
Relevance score + explanation
    ↓
Included / excluded from digest
    ↓
Audit event with reason
```

### Feedback and Memory Flow

```text
User feedback in Discord or panel
    ↓
Feedback handler classifies feedback
    ↓
If transient: update run-level preference only
If validated pattern: promote to agent-local memory
If broadly stable: promote to shared project memory
    ↓
Future ranking/composition uses promoted memory
```

## Patterns to Follow

### Pattern 1: Orchestrated Pipeline, Not Open-Ended Swarm
**What:** A single run coordinator invokes bounded services in order.  
**When:** v1 and near-term expansion.  
**Trade-offs:** Less “agentic magic,” much higher debuggability and repeatability.

Use the LLM inside steps where judgment helps:
- topic classification
- duplicate resolution tie-breaks
- story importance scoring
- digest wording

Do **not** use the LLM to decide the entire run plan from scratch each day.

### Pattern 2: Canonical Story as Primary Domain Object
**What:** Treat “story” as the durable object, not “article.”  
**When:** Any news or research aggregation workflow.  
**Trade-offs:** Requires more modeling up front, but fixes the core duplicate/noise problem.

Recommended object flow:

```text
source item → normalized item → canonical story → digest entry
```

This is the main reusable boundary for later research workflows too.

### Pattern 3: Audit Event as Source of Truth for Visibility
**What:** Discord-visible handoffs and control-panel traces should be rendered from the same event stream.  
**When:** Always.  
**Trade-offs:** Slightly more plumbing; much better consistency.

If Discord says “digest composition started,” the control panel should be able to show the same event with the same run ID.

### Pattern 4: Promotion-Based Memory
**What:** Logs are not memory; memory is curated from logs.  
**When:** Always.  
**Trade-offs:** More discipline, less silent degradation.

Recommended write policy:
- raw events stay in run history
- ranking explanations stay attached to stories/runs
- only validated preferences/patterns move into durable memory

## Anti-Patterns to Avoid

### Anti-Pattern 1: Starting with a Full Worker Mesh
**What people do:** Create many named agents with overlapping authority.  
**Why bad:** Hard to debug, hard to evaluate, and easy to hide weak domain logic behind prompts.  
**Instead:** Start with one orchestrator and 4-6 bounded services.

### Anti-Pattern 2: Treating Dedup as a UI Feature
**What people do:** Fetch many articles, summarize them, and only then try to “hide duplicates.”  
**Why bad:** The digest remains noisy because duplication was never resolved at the domain level.  
**Instead:** Build canonical story clustering before final ranking/composition.

### Anti-Pattern 3: Using One Shared Memory Bucket
**What people do:** Save everything into vectors/SQLite/files without class boundaries.  
**Why bad:** Retrieval quality decays and ranking behavior gets inconsistent.  
**Instead:** Keep run logs, story data, and promoted memory separate.

### Anti-Pattern 4: Overbuilding for Multi-User Too Soon
**What people do:** Add tenancy, roles, permissions, and generalized workspace models in v1.  
**Why bad:** Large surface area with no user value for the current slice.  
**Instead:** Design IDs and boundaries cleanly, but optimize implementation for one user.

## Build-Order Implications

The build order should mirror the actual risk.

### Phase 1: Runtime Skeleton and Traceability
- MicroClaw + Ollama wiring
- Discord adapter for outbound messages
- run IDs, event log, basic control-panel visibility
- manual trigger for one digest run

**Why first:** If you cannot inspect a run, every later issue becomes expensive.

### Phase 2: Intake and Canonical Story Pipeline
- source connectors
- normalized item schema
- raw item persistence
- canonical story creation
- duplicate clustering

**Why second:** This is the product’s real moat for the stated pain.

### Phase 3: Ranking and Digest Composition
- relevance scoring
- sectioning rules
- LLM summarization/compression
- citation/link formatting
- Discord digest formatting

**Why third:** Only valuable after the input quality is trustworthy.

### Phase 4: Feedback and Memory Promotion
- thumbs-up/down or command-based feedback
- ranking explanation capture
- promotion rules into agent-local/shared memory
- re-run with updated preferences

**Why fourth:** Personalization matters, but only after the basic digest works.

### Phase 5: Near-Term Expansion Layer
- reusable workflow definitions for “topic watch,” “tool watch,” or “research brief”
- shared intake/story/ranking infrastructure reused across workflows
- limited additional workers where boundaries are already proven

**Why fifth:** Expand from the stable core instead of inventing a platform first.

## Near-Term Expansion Structure

The architecture should expand by adding **new workflows over the same core services**, not by creating a separate system per use case.

Reusable core for later workflows:

- source intake
- canonical entity/story formation
- ranking/filtering
- brief composition
- feedback capture
- layered memory
- audit/event stream

Examples of future workflows that fit this structure:
- competitor update brief
- partner/prospect monitoring
- resource discovery feed
- post-idea generation from the story graph

## Scalability Considerations

| Concern | At v1 single user | At modest expansion | At large scale |
|---------|-------------------|---------------------|----------------|
| Orchestration | Single local orchestrator | Add queued jobs per workflow | Split workers only when contention appears |
| Storage | SQLite is fine | Partition raw items vs stories vs events | Move hot paths to stronger DB only if needed |
| LLM cost/latency | Local Ollama acceptable | Cache intermediate judgments | Introduce model routing if workloads multiply |
| Control panel | Simple run browser | Add filters, diff views, replay | Separate observability backend only later |

What breaks first is unlikely to be “number of agents.”  
It is more likely to be:

1. poor dedup quality
2. weak ranking criteria
3. noisy memory promotion
4. lack of run inspection

## Recommended Repository / Module Shape

```text
src/
├── app/
│   ├── scheduler/         # daily triggers, replays, backfills
│   ├── orchestration/     # run state machine, policies, visible routing
│   └── workflows/         # digest workflow definition, future research workflows
├── domain/
│   ├── sources/           # connectors + source-specific parsing
│   ├── stories/           # normalization, canonical story model, dedup
│   ├── ranking/           # scoring, filtering, explanation capture
│   ├── digest/            # composition, formatting, citation assembly
│   └── memory/            # layered memory + promotion policy
├── infrastructure/
│   ├── microclaw/         # runtime integration
│   ├── ollama/            # model gateway, prompts, embeddings
│   ├── persistence/       # SQLite stores, files, repositories
│   ├── discord/           # delivery adapter, command handling
│   └── observability/     # event log, traces, metrics
└── ui/
    └── control-panel/     # run review, audit, story inspection
```

## Recommendation

For v1, the best structure is:

- **MicroClaw as the local runtime**
- **one explicit digest workflow**
- **bounded internal services instead of a broad worker mesh**
- **canonical story formation as a first-class subsystem**
- **Discord + control panel backed by the same event log**
- **layered memory with strict promotion rules**

That gives you the smallest architecture that still matches the real product risk.  
It also leaves a clean path to expand into research workflows without rewriting the core.

## Sources

- `C:\Users\galzi\src\personal-agent-hub\.planning\PROJECT.md` — project scope and constraints
- `C:\Users\galzi\src\personal-agent-hub\.planning\diagrams\architecture-diagram.mmd` — current direction being stress-tested
- `C:\Users\galzi\src\personal-agent-hub\.planning\notes\architecture-repository-mapping.md` — MicroClaw-based component mapping
- `C:\Users\galzi\src\personal-agent-hub\.planning\notes\layered-memory-model.md` — current memory direction
- `C:\Users\galzi\src\personal-agent-hub\.planning\notes\visible-routing-architecture.md` — routing visibility direction
- MicroClaw README — channel-agnostic runtime, persistent memory, scheduled tasks, web control plane (official repo snapshot fetched 2026-04-11)
- Ollama API docs — local chat/generate/embeddings API surface (official docs snapshot fetched 2026-04-11)
