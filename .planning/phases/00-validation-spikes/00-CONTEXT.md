# Phase 0: Validation Spikes - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate that MicroClaw, Ollama, and the starter watchlist are sufficient for v1 before writing application code. This phase produces go/no-go decisions for each technology, not application features.

</domain>

<decisions>
## Implementation Decisions

### Spike Scope & Pass/Fail Criteria
- **D-01:** MicroClaw spike is a smoke test — verify 4 critical capabilities on Windows: scheduled task execution, Discord message posting, SQLite read/write, and control panel access. Pass = all 4 work. Fail = any one blocks.
- **D-02:** Ollama spike is a quick evaluation — run 10-15 representative tasks (ranking relevance, summarizing AI news, "why it matters" explanations). Pass/fail by user judgment: is the output usable or not?
- **D-03:** Watchlist spike is an automated feed scan — actually fetch the 9 feeds for the past week, list all items, and user reviews which important stories are present/missing. Pass = catches at least 50% of important AI news from that week.

### Fallback Strategy
- **D-04:** If MicroClaw fails → fall back to NanoClaw on WSL2. This trades the Windows-first constraint for a known-working runtime.
- **D-05:** If Ollama model quality fails → keep Ollama for embeddings and cheap tasks, add a remote provider (Claude or OpenAI API) for ranking and "why it matters" summaries only. STACK.md already anticipated this variant.
- **D-06:** If watchlist coverage falls below 50% → accept and move on. Coverage will improve organically as sources are added in later phases. Don't block Phase 1 on watchlist size.

### Spike Execution Approach
- **D-07:** Merge the 3 folded todos into the 3 roadmap spikes: MicroClaw+Ollama setup todo becomes the MicroClaw spike, visible-routing prototype folds in as a stretch goal, rescoping exercise becomes a lightweight output of all three spikes (what did we learn?).
- **D-08:** Run spikes sequentially: MicroClaw first (everything depends on it), then Ollama quality evaluation, then watchlist backtest. Natural dependency chain.
- **D-09:** Visible-routing prototype is a stretch goal within the MicroClaw spike — test it if time allows, but it doesn't block the go/no-go decision. The 4 core capabilities are the hard requirements.

### Ollama Model Selection
- **D-10:** Target the ~32B parameter range for the chat/ranking model (e.g., Qwen3-Coder:32B or Gemma 4:27B). Good quality-to-resource balance.
- **D-11:** Start with one model, expand if needed — pick the most promising ~32B model, evaluate it. Only test a second model if the first fails the quality bar.
- **D-12:** Use a separate dedicated embedding model (e.g., nomic-embed-text or mxbai-embed-large) for sqlite-vec semantic retrieval. The chat model handles ranking/summarization only.

### Claude's Discretion
- Claude picks the specific first-choice ~32B Ollama model based on current benchmarks and community feedback for ranking/summarization tasks.
- Claude picks the specific embedding model based on what works well with sqlite-vec and Ollama.

### Folded Todos
- **Set up MicroClaw + Ollama prototype** — Fork, build, configure Ollama, verify chat/scheduling/sub-agents/MCP. Merged into the MicroClaw spike as its core execution.
- **Prototype MicroClaw visible-routing layer** — Prove hybrid coordination with chat announcements + panel traces. Merged into the MicroClaw spike as a stretch goal.
- **Rescope v1 around one visible workflow** — Prove one end-to-end workflow before expanding. Becomes a lightweight synthesis output after all three spikes complete.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Risk Analysis
- `.planning/RISK-REVIEW.md` — Full risk register (R1-R10) with assumption analysis. R1 (MicroClaw), R3 (Ollama quality), R4 (watchlist coverage) directly drive Phase 0 scope.

### Technology Stack
- `.planning/research/STACK.md` — Recommended stack with versions, confidence levels, and fallback variants. Defines MicroClaw v0.1.50, Ollama v0.20.5, sqlite-vec v0.1.9, and all supporting libraries.
- `.planning/research/ARCHITECTURE.md` — System architecture including visible routing, layered memory, and control panel design.

### Project Context
- `.planning/PROJECT.md` — Core value, constraints, key decisions. Includes the planning-to-execution ratio guard (R6 mitigation).
- `.planning/research/PITFALLS.md` — 12 domain-specific pitfalls that inform what the spikes should watch for.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — this is a greenfield repo with no application code yet.

### Established Patterns
- None — Phase 0 will establish the first patterns.

### Integration Points
- MicroClaw will be the first external dependency introduced.
- Ollama will be the second, configured through MicroClaw.
- Python 3.12 + uv will be needed for the watchlist backtest spike (feedparser, httpx).

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for each spike. The key constraint is keeping spikes lightweight (smoke tests and quick evaluations, not exhaustive benchmarks).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

### Reviewed Todos (not folded)
No todos were reviewed but deferred — all three matched todos were folded into scope.

</deferred>

---

*Phase: 00-validation-spikes*
*Context gathered: 2026-04-12*
