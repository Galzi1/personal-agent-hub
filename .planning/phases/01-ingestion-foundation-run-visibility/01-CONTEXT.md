# Phase 1: Ingestion Foundation & Run Visibility - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish a local-first daily digest intake from a curated multi-source watchlist and make each run outcome visible and traceable. This phase defines the intake boundary, the run-visibility behavior, and the traceability model for the first workflow; canonical story formation, ranking, digest composition quality, and feedback controls belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Source watchlist shape
- **D-01:** Phase 1 intake uses official product sources plus a small curated industry layer, not official-only intake and not a broad community/social sweep.
- **D-02:** Start with a small, high-trust seed watchlist that can expand later rather than trying to launch with broad coverage.
- **D-03:** The non-official layer should mostly be high-signal AI news and product trackers, with only a tiny allowlist of proven trend-watchers.
- **D-04:** Sources without a clean feed or API are skipped in Phase 1 unless they later become important enough to justify a fallback path.
- **D-05:** The starter watchlist is managed through a simple local config/allowlist, not through Discord commands or a control-panel editing UI.
- **D-06:** The watchlist enforces trust tiers: official sources highest, curated trackers next, trend-watchers lowest.
- **D-07:** Official blogs/changelogs and GitHub release feeds must be included in the starter watchlist.

### Run visibility in Discord
- **D-08:** Run-status messages live in a dedicated shared agent-status side channel; the digest channel stays clear and focused on the delivered digest.
- **D-09:** Discord-visible narration should cover only major milestones: run start, ingestion complete, and final outcome.
- **D-10:** Successful runs should post a concise summary with key counts and a link back to the deeper trace.
- **D-11:** Failed runs and no-qualifying-item runs should both post explicit status messages with a short reason and a trace link.

### Run trace details
- **D-12:** Each visible run uses a human-readable label with date/time plus a short run ID, not timestamp-only or opaque internal identifiers.
- **D-13:** Status-message trace links should land on the exact run's raw event/log view.
- **D-14:** The default trace surface is an append-only event timeline with timestamps, event types, and outcome markers.
- **D-15:** Every retry or manual rerun gets its own run label and short ID, with links between related runs rather than overwriting a day-level identity.

### Schedule and rerun behavior
- **D-16:** The scheduled digest run executes every day at **08:00 local time**.
- **D-17:** Manual on-demand reruns are allowed and must be clearly labeled as separate runs.
- **D-18:** A scheduled failure gets one automatic retry after a short delay; if it still fails, the failure is surfaced clearly.

### the agent's Discretion
- Exact starter source names within the chosen trust tiers and source types.
- Exact local config file shape and storage location for the Phase 1 watchlist.
- Exact short run ID format and human-readable naming convention.
- Exact event schema fields and UI presentation details within the append-only timeline model.
- Exact delay before the single automatic retry.

### Folded Todos
- **Prototype MicroClaw visible-routing layer** — folded into scope so major handoffs can be narrated in chat while deeper traces remain available in the control panel/log layer.
- **Set up MicroClaw + Ollama prototype** — folded into scope because Phase 1 depends on proving the Windows-first MicroClaw + Ollama foundation before intake and visibility behavior are implemented.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and product constraints
- `.planning/ROADMAP.md` §Phase 1 — Defines the phase goal, requirements, and success criteria for intake plus run visibility.
- `.planning/PROJECT.md` — Defines the Discord-first, local-first, visible-routing, and single-user constraints that shape this phase.
- `.planning/REQUIREMENTS.md` — Defines the relevant requirement coverage for `SRC-01` and `DGST-04`.
- `.planning/STATE.md` — Captures the current phase focus and the unresolved cadence/planning concerns that this context resolves.

### Foundation and visibility architecture
- `.planning/notes/architecture-repository-mapping.md` — Locks MicroClaw as the foundation and keeps NanoClaw only as a fallback path.
- `.planning/notes/visible-routing-architecture.md` — Defines the split between chat-visible routing and the control panel as the forensic layer.
- `.planning/research/ARCHITECTURE.md` — Recommends the workflow-oriented local monolith, append-only event trail, and event-source-of-truth visibility model.
- `.planning/research/STACK.md` — Recommends MicroClaw + Ollama + SQLite/sqlite-vec, Discord via MicroClaw, and RSS/API-first intake.

### Folded implementation anchors
- `.planning/todos/pending/prototype-microclaw-visible-routing-layer.md` — Concrete success criteria for the chat-visible routing layer folded into this phase.
- `.planning/todos/pending/setup-microclaw-ollama-prototype.md` — Concrete success criteria for the MicroClaw + Ollama foundation folded into this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **MicroClaw native runtime capabilities** (`.planning/research/STACK.md`) — Discord delivery, scheduler, control plane, MCP, SQLite/sqlite-vec, and Ollama support cover most of the Phase 1 foundation without introducing a second app or orchestration layer.
- **Visible-routing architecture note** (`.planning/notes/visible-routing-architecture.md`) — Defines the thin routing/policy layer above MicroClaw and the chat-vs-control-panel split.
- **Folded implementation todos** (`.planning/todos/pending/prototype-microclaw-visible-routing-layer.md`, `.planning/todos/pending/setup-microclaw-ollama-prototype.md`) — Provide concrete objectives for foundation setup and status visibility.

### Established Patterns
- Use **MicroClaw as the execution core**, not a wrapper around another orchestration framework.
- Prefer **RSS/API-first intake** with scraping as an exception path, not the default ingestion strategy.
- Use **chat-visible status plus deeper control-panel traces** from the same underlying run/event history.
- Keep Phase 1 scoped to **one visible workflow**, not a full worker mesh.

### Integration Points
- **Digest delivery surface:** Discord digest channel remains focused on the delivered digest.
- **Status surface:** Dedicated shared agent-status side channel carries run milestones and outcome messages.
- **Trace surface:** Control panel raw event/log view is the landing target for trace links.
- **Local runtime foundation:** MicroClaw + Ollama on Windows with SQLite-backed run/event persistence.
- **Watchlist management:** Local config/allowlist defines the curated source boundary.

</code_context>

<specifics>
## Specific Ideas

- "A side channel for agent status, that will be shared by all the agents later on. Keep the digest channel clear and focused."
- Trace links should land directly on the **raw event/log view** for the exact run.
- The daily scheduled run should target **08:00 local**.
- Manual reruns should exist, but they must be clearly labeled as separate runs rather than replacing the scheduled run's identity.

</specifics>

<deferred>
## Deferred Ideas

### Reviewed Todos (not folded)
- **Rescope v1 around one visible workflow** — Reviewed but not folded because the current roadmap and Phase 1 boundary already assume one visible workflow; it does not add extra implementation scope to this phase.

No additional deferred feature ideas surfaced during discussion.

</deferred>

---

*Phase: 01-ingestion-foundation-run-visibility*
*Context gathered: 2026-04-11*
