# Phase 0: Validation Spikes - Context

**Gathered:** 2026-04-12
**Updated:** 2026-04-24 (post-Plan 00-01 GO; OpenRouter pivot + Plan 01 learnings locked in)
**Status:** Ready for Plan 00-02 rewrite + execution

<domain>
## Phase Boundary

Validate that MicroClaw, the selected LLM provider, and the starter watchlist are sufficient for v1 before writing application code. This phase produces go/no-go decisions for each technology, not application features.

**Status update (2026-04-24):**
- Plan 00-01 (MicroClaw smoke test) - **COMPLETE, GO**. R1 closed.
- Plan 00-02 (LLM model quality) - **pending rewrite**; pivoted from local Ollama to OpenRouter per D-13/D-14.
- Plan 00-03 (watchlist backtest) - pending execution.

</domain>

<decisions>
## Implementation Decisions

### Spike Scope & Pass/Fail Criteria
- **D-01:** MicroClaw spike is a smoke test - verify 4 critical capabilities on Windows: scheduled task execution, Discord message posting, SQLite read/write, and control panel access. Pass = all 4 work. Fail = any one blocks. *(COMPLETE 2026-04-23: all 4 PASS.)*
- **D-02:** LLM model-quality spike is a quick evaluation - run 10-15 representative tasks (ranking relevance, summarizing AI news, "why it matters" explanations). Pass/fail by user judgment: is the output usable or not? *(Original wording referenced Ollama; reinterpreted 2026-04-24 per D-13 to target OpenRouter-hosted models.)*
- **D-03:** Watchlist spike is an automated feed scan - actually fetch the 9 feeds for the past week, list all items, and user reviews which important stories are present/missing. Pass = catches at least 50% of important AI news from that week.

### Fallback Strategy
- **D-04:** If MicroClaw fails → fall back to NanoClaw on WSL2. *(Moot: MicroClaw GO recorded 2026-04-23.)*
- **D-05:** ~~If Ollama model quality fails → keep Ollama for embeddings and cheap tasks, add a remote provider for ranking and "why it matters" summaries only.~~ **SUPERSEDED 2026-04-24 by D-13:** Remote-only via OpenRouter is now the baseline, not a fallback. No hybrid with local Ollama.
- **D-06:** If watchlist coverage falls below 50% → accept and move on. Coverage will improve organically as sources are added in later phases. Don't block Phase 1 on watchlist size.

### Spike Execution Approach
- **D-07:** Merge the 3 folded todos into the 3 roadmap spikes: MicroClaw+LLM-provider setup todo became the MicroClaw spike, visible-routing prototype folded in as a stretch goal, rescoping exercise becomes a lightweight output of all three spikes (what did we learn?).
- **D-08:** Run spikes sequentially: MicroClaw first (everything depends on it), then LLM quality evaluation, then watchlist backtest. Natural dependency chain.
- **D-09:** Visible-routing prototype is a stretch goal within the MicroClaw spike - test it if time allows, but it doesn't block the go/no-go decision. *(SKIPPED per Plan 00-01 results; deferred to Phase 1+.)*

### LLM Provider & Model Selection *(revised 2026-04-24)*
- **D-10:** ~~Target the ~32B parameter range for the chat/ranking model locally via Ollama (Qwen3-Coder:32B or Gemma 4:27B).~~ **SUPERSEDED by D-14:** OpenRouter is the sole LLM provider; local Ollama chat path dropped. 32B class local inference is not viable with 6.4 GB free RAM + AMD Radeon 890M (512 MB VRAM, no useful GPU offload).
- **D-11:** ~~Start with one Ollama model, expand if needed.~~ **SUPERSEDED by D-15:** Per-task model selection replaces single-model-for-all.
- **D-12:** ~~Use a separate local embedding model via Ollama (e.g., nomic-embed-text).~~ **SUPERSEDED by D-16:** Embeddings via OpenRouter too.
- **D-13:** **Remote-only for all LLM tasks via OpenRouter.** Ranking, summarization, "why it matters", and embeddings all run against OpenRouter-hosted models. Rationale: Windows CPU inference with 6.4 GB free RAM cannot host a 32B model without swap-thrashing; GPU offload not viable. OpenRouter provides unified billing, auth, and per-task model flexibility. Trade-off: local-first privacy premise relaxed to "secrets-first" (API keys local; OpenRouter retains inference-session metadata only).
- **D-14:** OpenRouter is the **sole** LLM provider for chat and embeddings. No direct Anthropic / OpenAI / Google / Cohere API clients elsewhere in the app. Benefits: single API key, single billing surface, single retry/rate-limit policy, portable model switching without code changes.
- **D-15:** **Per-task model selection.** Each task type (ranking, summarization, why_it_matters, embedding, and any future task types) has its own model assignment, independently tunable. Different quality / cost / latency profiles per task.
- **D-16:** **Embedding starter:** `cohere/embed-multilingual-v3.0` on OpenRouter (1024-dim). Plan 00-02 verifies OpenRouter's embedding endpoint actually exposes this model; if unavailable, fallback order is `voyage-3` → `openai/text-embedding-3-large` → record finding and escalate to a separate embedding provider decision.
- **D-17:** **Model configuration is externalized to a config file today and surfaced via the control panel later.** No hardcoded model IDs in application code. Config-driven selection is a first-class framework concern, not an afterthought. Any code that hardcodes a model ID is a regression.
- **D-18:** **Starter model assignments** (user-specified 2026-04-24; Plan 00-02 must verify each is available via OpenRouter `/v1/models` before running the eval):
  - `ranking` → **Gemini 3 Flash Preview**
  - `summarization` → **Nemotron 3 Super**
  - `why_it_matters` → **GPT-5.4**
  - `embedding` → **cohere/embed-multilingual-v3.0**

  If any starter is unavailable on OpenRouter at spike execution time, Plan 00-02 records a finding and the spike falls back to the nearest equivalent: `google/gemini-2.5-flash` / `nvidia/nemotron-4-340b-instruct` / `openai/gpt-5` / `voyage-3` respectively. Final selection may change after the spike based on quality/cost data.

### Configuration & Secrets Layout *(new 2026-04-24)*
- **D-19:** **Single `config/` folder at repo root holds all YAML configuration.** `microclaw.config.yaml` relocates from repo root to `config/microclaw.config.yaml`. `models.yaml` lives alongside at `config/models.yaml`. Future YAML config files (logging, runtime tuning, etc.) go in the same folder. Whole folder gitignored if any file holds secrets; granular `.gitignore` entries used if some files are safe to track. Relocation of `microclaw.config.yaml` is part of Plan 00-02 setup (or a Plan 01 follow-up commit) and must verify MicroClaw can read from the new path (likely via `microclaw --config ./config/microclaw.config.yaml`).
- **D-20:** **OpenRouter API key stored inside `config/microclaw.config.yaml`** alongside the Discord bot token and (legacy) Anthropic key. Single secrets file, already gitignored (per commit `10eb975`). Both MicroClaw runtime and Python spike/app code read from this file. Control panel edits it in place in later phases.
- **D-21:** **`config/models.yaml` schema** (owned by Plan 00-02 to define formally; minimum shape):
  ```yaml
  tasks:
    ranking:        { model: "<openrouter-id>" }
    summarization:  { model: "<openrouter-id>" }
    why_it_matters: { model: "<openrouter-id>" }
    embedding:      { model: "<openrouter-id>" }
  ```
  Python loader reads at startup; future control panel edits via UI and writes the same file. Optional per-task fields (temperature, max_tokens, etc.) allowed but not required.

### Plan 00-02 Budget & Safety *(new 2026-04-24)*
- **D-22:** **$20 hard cap on Plan 00-02 OpenRouter spend.** Spike aborts if cumulative cost approaches cap. Expected actual: ~$0.30 for single-pass 15-task evaluation against the D-18 starters. Budget headroom allows multi-model comparison if any starter fails the quality bar.

### MicroClaw Runtime Contracts *(new 2026-04-24, from Plan 00-01 F1)*
- **D-23:** **@-mention is the locked contract for MicroClaw bot-receiver flows in Discord channels.** Plain-text channel messages are silently dropped by MicroClaw's router. Phase 1+ channel-based inbound flows (user asks bot questions, reacts to digest items) MUST use `@<bot-name> <prompt>` format. DM path treated as untested alternative; no inbound flow depends on DMs until verified. Evidence: Plan 00-01 Finding F1 in `00-01-SPIKE-RESULTS.md`.
- **D-24:** **Phase 1 scope is daily digest outbound-only.** All inbound user flows (Q&A, feedback-on-digest) deferred to Phase 2+. Consequence: F1 does not block Phase 1; the @-mention contract only constrains Phase 2+ discuss-phases.

### Claude's Discretion
- Claude picks OpenRouter client approach for Plan 02 (likely `httpx`-based raw HTTP vs OpenRouter's official SDK if one exists in Python).
- Claude picks retry / rate-limit / timeout defaults for the OpenRouter HTTP client.
- Claude picks exact YAML loader library (PyYAML vs ruamel.yaml) for `config/models.yaml`.
- Claude proposes model IDs for any task type added after D-18 that the user has not specified.

### Folded Todos
- **Set up MicroClaw + Ollama prototype** - Merged into MicroClaw spike (COMPLETE). "Ollama" portion is now re-interpreted as "LLM provider" and routes through OpenRouter per D-13.
- **Prototype MicroClaw visible-routing layer** - Merged into MicroClaw spike as stretch goal. SKIPPED per 00-01 results; remains deferred.
- **Rescope v1 around one visible workflow** - Becomes a lightweight synthesis output after all three spikes complete.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Risk Analysis
- `.planning/RISK-REVIEW.md` - Full risk register (R1-R10). R1 (MicroClaw) CLOSED 2026-04-23. R3 description now reads "OpenRouter-hosted model quality unverified" rather than "Ollama model quality unverified"; mitigation still runs through Plan 00-02.

### Technology Stack
- `.planning/research/STACK.md` - Recommended stack with versions, confidence levels, and fallback variants. **Needs update 2026-04-24:** Ollama chat-model entries superseded; add OpenRouter SDK/client. Embedding stack entry replaced with Cohere via OpenRouter.
- `.planning/research/ARCHITECTURE.md` - System architecture. D-17 establishes model-config UI as a first-class Phase 2+ control panel feature.

### Project Context
- `.planning/PROJECT.md` - Core value, constraints, key decisions. Includes the planning-to-execution ratio guard (R6 mitigation).
- `.planning/research/PITFALLS.md` - 12 domain-specific pitfalls that inform what the spikes should watch for.

### Phase 0 Artifacts
- `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md` - 4-test MicroClaw results + 4 findings (F1-F4). F1 is the @-mention contract locked in D-23.
- `.planning/phases/00-validation-spikes/00-01-SUMMARY.md` - Plan 01 completion summary (environment: 32 GB total RAM, 6.4 GB free at setup, AMD Radeon 890M).

### External Service Documentation
- OpenRouter API docs: https://openrouter.ai/docs - Plan 00-02 must read before rewrite to confirm available models, embedding endpoint, auth pattern, rate limits, streaming support.
- OpenRouter models list: https://openrouter.ai/models - Verify D-18 starter IDs at spike execution time.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `C:\Users\galzi\.microclaw\microclaw.db` - SQLite runtime DB populated by Plan 01 tests. Phase 1+ app code shares this DB path per MicroClaw's standard runtime layout.
- `microclaw.config.yaml` (at repo root as of Plan 01; relocating to `config/` per D-19) - holds Discord bot token + Anthropic API key; soon adds OpenRouter key. Gitignored per commit `10eb975`.

### Established Patterns
- **Secrets file gitignored, not relocated to `$HOME\.microclaw\`** (Plan 01 decision). Keep pattern: `config/microclaw.config.yaml` gitignored; no separate project-secrets split.
- **Validation spikes document *findings*, not just PASS/FAIL**, to surface usage contracts for downstream phases. D-23 (F1 lock-in) is the first cross-phase output of this pattern.

### Integration Points
- MicroClaw runtime: validated on Windows 11 x86_64. Receives Discord + Anthropic tokens via `microclaw.config.yaml`; will also receive OpenRouter key.
- OpenRouter API: new for Plan 00-02. Single provider for chat + embeddings per D-14. HTTP client needed; default to `httpx` in Python 3.12.
- Python 3.12 + uv: still needed for watchlist backtest (feedparser, httpx) and Plan 02 OpenRouter spike.

</code_context>

<specifics>
## Specific Ideas

- User-named starter models (D-18) supersede Claude's proposed defaults. Plan 02 must verify each on OpenRouter's `/v1/models` endpoint and log an "alt-picked" finding if it substitutes a fallback.
- "All YAML config in a single folder, not scattered" is a load-bearing UX preference (D-19). Violate only with explicit user approval.
- Model selection must be easy to change now (file edit) and later (control panel UI). Hardcoded model IDs in Python source are a regression.

</specifics>

<deferred>
## Deferred Ideas

- **Control panel model-selection UI** - Design into the control panel work when the panel phase starts. Not Phase 0 scope; tracked here so the relevant Phase's discuss-phase surfaces it.
- **DM-based bot-receiver flow as an alternative to @-mention** - untested alternative path for future inbound flows. Revisit if @-mention UX proves friction-heavy in Phase 2+.
- **Prefix-based or channel-whitelisted MicroClaw routing** - alternative to @-mention contract; investigate only if @-mention UX fails user-testing.
- **STACK.md rewrite** to reflect OpenRouter-only baseline. Small follow-up, not blocking Phase 0 completion.
- **Relocation of `microclaw.config.yaml` from repo root to `config/`** - tied to D-19. Happens as part of Plan 00-02 setup or a Plan 01 follow-up commit.

### Reviewed Todos (not folded)
No todos were reviewed but deferred - all three originally matched todos remain folded into scope (Plan 01 + future spike synthesis output).

</deferred>

---

*Phase: 00-validation-spikes*
*Context gathered: 2026-04-12*
*Updated: 2026-04-24 - OpenRouter pivot + Plan 01 learnings locked in*
