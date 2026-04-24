# Phase 0: Validation Spikes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 00-validation-spikes
**Areas discussed:** Spike scope & pass/fail criteria, Fallback strategy, Spike execution approach, Ollama model selection

---

## Spike Scope & Pass/Fail Criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Smoke test | Verify 4 critical capabilities on Windows: scheduled task, Discord post, SQLite read/write, control panel access | ✓ |
| Feature exercise | Go deeper: test sub-agent spawning, MCP integration, embed formatting, long-message splitting, error recovery | |
| Production rehearsal | Build a mini end-to-end flow (schedule → fetch RSS → store → post to Discord) | |

**User's choice:** Smoke test
**Notes:** Binary pass/fail on 4 core capabilities.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Quick evaluation | Run 10-15 representative tasks, score pass/fail by judgment | ✓ |
| Structured benchmark | Build test corpus with expected outputs, score quantitatively | |
| Comparative evaluation | Run same tasks against 2-3 Ollama models AND one cloud model as ceiling reference | |

**User's choice:** Quick evaluation
**Notes:** User judgment on output quality, not quantitative benchmarks.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Manual recall check | Recall 10-15 AI news items from last week, check which ones 9-feed watchlist would catch | |
| Automated feed scan | Actually fetch 9 feeds for past week, list items, review present/missing | ✓ |
| Skip watchlist spike | Focus spike effort on MicroClaw and Ollama | |

**User's choice:** Automated feed scan
**Notes:** More objective than manual recall - uses real feed data.

---

| Option | Description | Selected |
|--------|-------------|----------|
| 70% coverage | If 9 feeds catch at least 70% of important AI news, watchlist is good enough | |
| 50% coverage | Lower bar - just needs to prove it catches something useful | ✓ |
| You decide | Claude sets threshold based on scan results | |

**User's choice:** 50% coverage
**Notes:** Low bar since expansion is planned anyway. Don't block on watchlist size.

---

## Fallback Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| NanoClaw on WSL2 | Switch to NanoClaw on WSL2, trade Windows-first constraint for known-working runtime | ✓ |
| Custom stack | Assemble from discord.py + APScheduler + SQLite | |
| Debug and retry | Try to fix the MicroClaw issue first, only pivot if unfixable within a day | |
| You decide | Claude picks based on which capability failed | |

**User's choice:** NanoClaw on WSL2
**Notes:** Preferred fallback for MicroClaw failure.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Remote provider for synthesis only | Keep Ollama for embeddings, add Claude/OpenAI API for ranking and summaries | ✓ |
| Try a bigger Ollama model | Jump from 8B to 32B+ before pivoting to remote | |
| Go fully remote | Drop Ollama for LLM tasks, use cloud API for everything | |
| You decide | Claude picks based on which tasks failed | |

**User's choice:** Remote provider for synthesis only
**Notes:** Hybrid approach preserves local-first principle for most tasks.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Expand watchlist and retest | Add more feeds targeting gaps until coverage hits bar | |
| Accept and move on | Coverage improves organically in later phases | ✓ |
| Add non-RSS sources | Bring in Apify scraping or X/Twitter lists as Phase 0 scope | |

**User's choice:** Accept and move on
**Notes:** Watchlist is non-blocking - easy to expand later.

---

## Spike Execution Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Merge into 3 spikes | Setup todo → MicroClaw spike, routing todo → stretch goal, rescope todo → synthesis output | ✓ |
| Keep as 6 separate tasks | Each spike and todo as its own discrete work item | |
| Merge into 2 spikes | Combine MicroClaw + routing + Ollama setup into one big spike | |

**User's choice:** Merge into 3 spikes
**Notes:** Natural mapping between todos and roadmap spikes.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Sequential: MicroClaw first | MicroClaw → Ollama → watchlist, natural dependency chain | ✓ |
| MicroClaw first, then parallel | MicroClaw first, then Ollama and watchlist in parallel | |
| All parallel | Start all three simultaneously | |

**User's choice:** Sequential: MicroClaw first
**Notes:** Everything depends on MicroClaw, so it must go first.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Stretch goal | Test routing if time allows, doesn't block go/no-go | ✓ |
| Hard requirement | Routing capability is part of pass/fail criteria | |
| Separate follow-up spike | 4th mini-spike after MicroClaw passes | |

**User's choice:** Stretch goal
**Notes:** 4 core capabilities are the hard requirements; routing is nice-to-have.

---

## Ollama Model Selection

| Option | Description | Selected |
|--------|-------------|----------|
| ~32B parameter range | Qwen3-Coder:32B, Gemma 4:27B - good quality/resource balance | ✓ |
| ~8B parameter range | Llama 3.1:8B, Qwen3:8B - faster but lower quality ceiling | |
| Largest feasible | 70B+ if GPU can handle it | |
| Not sure yet | Test 2-3 size classes during spike | |

**User's choice:** ~32B parameter range
**Notes:** Needs ~20GB VRAM. STACK.md mentions these models.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Start with one, expand if needed | Pick most promising ~32B model, only test second if first fails | ✓ |
| Compare 2-3 models | Head-to-head on same tasks | |
| You decide | Claude picks based on benchmarks | |

**User's choice:** Start with one, expand if needed
**Notes:** Efficient - don't over-invest in model comparison.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Separate embedding model | Dedicated small model (nomic-embed-text, mxbai-embed-large) for sqlite-vec | ✓ |
| Same model for everything | Use 32B model's embedding endpoint for both tasks | |
| You decide | Claude picks embedding model | |

**User's choice:** Separate embedding model
**Notes:** Standard practice - embedding models are specialized.

---

## Claude's Discretion

- Specific first-choice ~32B Ollama model selection
- Specific embedding model selection

## Deferred Ideas

None - discussion stayed within phase scope.

## Folded Todos

All three matched todos were folded into Phase 0 scope:
- Set up MicroClaw + Ollama prototype → MicroClaw spike core
- Prototype MicroClaw visible-routing layer → MicroClaw spike stretch goal
- Rescope v1 around one visible workflow → synthesis output after all spikes

---

# Update Session - 2026-04-24

**Trigger:** `/gsd-discuss-phase 0` re-run post Plan 00-01 GO. Purpose: reconcile Plan 00-02 contradictions (body mixed OpenRouter API calls with `ollama run` CLI) and lock Plan 00-01 Finding F1 as a cross-phase contract.
**Areas discussed:** Ollama local vs OpenRouter; @-mention as Phase 1 constraint; API key / secrets management; Model-per-task config file shape; Cost ceiling for Plan 02; Starter model assignments; Config folder naming & MicroClaw relocation; Per-task model selection timing

---

## Ollama local vs OpenRouter

### Q1 - Which target should Plan 00-02 evaluate?

| Option | Description | Selected |
|--------|-------------|----------|
| Local Ollama only | Stick with D-10: local Qwen3 32B via `ollama run`. Honest test of local-only constraint. | |
| OpenRouter only (pivot) | Supersede D-10: evaluate model quality via OpenRouter API. Removes RAM risk. | ✓ |
| Hybrid: test both | Run same 10-15 tasks against BOTH local Ollama AND OpenRouter. | |
| Local first, remote on RAM fail | Attempt local Qwen3 32B load. If OOM or >30s/token latency, auto-fall to OpenRouter. | |

**User's choice:** OpenRouter only (pivot)
**Notes:** RAM constraint (6.4 GB free, 32B needs ~20 GB) plus no useful GPU offload on AMD Radeon 890M make local infeasible.

### Q2 - New default for Phase 2+ LLM workloads if local fails?

| Option | Description | Selected |
|--------|-------------|----------|
| D-05 as-is (hybrid) | Ollama for embeddings + cheap tasks; remote for ranking + summarization. | |
| Remote-only for all LLM tasks | Drop local Ollama for chat entirely. | ✓ |
| Keep local, accept quality hit | Smaller local model (7B/14B). | |
| Defer to Plan 02 result | No pre-commit. | |

**User's choice (free text):** "Remote-only for all LLM tasks. We'll select different models with different capabilities and pricing for each task, all accessible via OpenRouter."
**Notes:** Drives D-13, D-14, D-15.

### Q3 - Where should embeddings live now?

| Option | Description | Selected |
|--------|-------------|----------|
| OpenRouter embeddings too | Single provider. Pick best available OpenRouter embedding. | ✓ |
| Local Ollama for embeddings | Narrow hybrid (nomic-embed-text local; chat remote). | |
| Dedicated embedding provider | OpenAI/Voyage/Cohere direct. Adds a third vendor. | |
| Defer to Plan 02 | Evaluate both side-by-side. | |

**User's choice:** OpenRouter embeddings too
**Notes:** Drives D-16. Single-vendor posture preserved.

### Q4 - Per-task model selection strategy?

| Option | Description | Selected |
|--------|-------------|----------|
| One strong model, all tasks | Flagship on OpenRouter for all 15 eval tasks. | |
| Per-task model, per-task spike | Pre-assigned models per task. | |
| Tiered eval: cheap first, escalate | Start cheapest; escalate on fail. | |
| User picks model list | Explicit 2-3 candidates run in parallel. | |
| (Free text - user-specified) | Per-task model WITH mandatory configurability via file now and control panel later. | ✓ |

**User's choice (free text):** "We will use per-task model but I MUST be able to configure and pick the model for EACH task easily, both now (via a configuration file) and later on (via the control panel)"
**Notes:** Drives D-15, D-17, D-19, D-21. Establishes config-driven model selection as a first-class framework concern.

---

## @-mention as Phase 1 constraint

### Q1 - How should F1 be locked at Phase 0 level?

| Option | Description | Selected |
|--------|-------------|----------|
| Lock @-mention UX as the contract | Phase 1 bot-receiver flows require @-mention in channels. | ✓ |
| Lock + require DM viability test | Same lock, but add a Phase 1 pre-condition: verify DM path first. | |
| Lock + investigate routing modes | Lock @-mention as baseline; schedule investigation of prefix-based/whitelisted routing. | |
| Don't lock here - defer to Phase 1 discuss | Note F1 but don't bind Phase 1. | |

**User's choice:** Lock @-mention UX as the contract
**Notes:** Drives D-23.

### Q2 - Which Phase 1 flow types in scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Daily digest only | Outbound-only. @-mention constraint does not apply. | |
| User feedback on digest | Inbound - needs @-mention design. | |
| User-initiated Q&A | Inbound - needs @-mention design. | |
| Defer all inbound to later phase | Phase 1 = daily digest only. | ✓ |

**User's choice:** Defer all inbound to later phase
**Notes:** Drives D-24. F1 does not bind Phase 1.

---

## API key + secrets management

### Q1 - Where should the OpenRouter API key be stored?

| Option | Description | Selected |
|--------|-------------|----------|
| Inside `microclaw.config.yaml` | Single source of truth; already gitignored. | ✓ |
| Separate `.env` at repo root | Standard Python pattern; friction for control panel later. | |
| Separate `secrets.yaml` | Readable YAML, gitignored. Clean separation. | |
| System env var only | Max security; session-scoped friction. | |

**User's choice:** Inside microclaw.config.yaml
**Notes:** Drives D-20.

---

## Model-per-task config file shape

### Q1 - Where does the model-per-task config file live?

| Option | Description | Selected |
|--------|-------------|----------|
| `config/models.yaml` | New repo-root dir `config/`. | |
| Nested in `microclaw.config.yaml` | Couples MicroClaw schema with app model selection. | |
| `.planning/models.yaml` | Unusual - .planning/ is GSD-owned docs. | |
| `pah/config/models.yaml` | Project-side package namespace. | |
| (Free text - user-specified) | Separate `models.yaml` but ALL YAML config in a SINGLE folder. | ✓ |

**User's choice (free text):** "I want it to be in a separate configuration file (like `models.yaml`) but I want ALL of the configuration yaml files to be in a single folder, not scattered around the repo"
**Notes:** Drives D-19, D-21. Implies relocation of `microclaw.config.yaml`.

---

## Cost ceiling for Plan 02

### Q1 - Budget cap for Plan 00-02 OpenRouter spike?

| Option | Description | Selected |
|--------|-------------|----------|
| $5 hard cap | Strict. Limits to ~1 model. | |
| $20 cap | Reasonable. ~$6–$15 typical + headroom. | ✓ |
| $50 cap | Loose. Multi-model exploration. | |
| No cap, user approves each batch | Manual gate. | |

**User's choice:** $20 cap
**Notes:** Drives D-22. Expected actual spend ~$0.30.

---

## Starter model assignments

### Q1 - Lock specific starter OpenRouter models per task type now, or defer?

| Option | Description | Selected |
|--------|-------------|----------|
| Lock starters now, allow override | CONTEXT.md names starters; Plan 02 runs these; override at exec time OK. | ✓ |
| Defer to Plan 02 execution time | Plan 02 prompts interactively per task. | |
| List 2-3 candidates per task | Plan 02 runs all and compares. | |
| Claude picks based on benchmarks | Defer to Claude; user edits before Plan 02. | |

**User's choice:** Lock starters now, allow override

### Q2a - Ranking model

| Option | Description | Selected |
|--------|-------------|----------|
| Claude Sonnet 4.6 (recommended) | Strong instruction-following + nuanced comparison. | |
| GPT-5 | Top reasoning on latest benchmarks. Higher cost. | |
| Gemini 2.5 Pro | 2M context, fast, competitive. | |
| (Free text) | Gemini 3 Flash Preview | ✓ |

**User's choice:** Gemini 3 Flash Preview
**Notes:** Plan 02 verifies availability on OpenRouter `/v1/models`; fallback `google/gemini-2.5-flash`.

### Q2b - Summarization model

| Option | Description | Selected |
|--------|-------------|----------|
| Claude Haiku 4.5 (recommended) | Cheap, fast, accurate. | |
| Gemini 2.5 Flash | Cheaper; faster TTFT. | |
| GPT-4o-mini | Known-good summaries. | |
| (Free text) | Nemotron 3 Super | ✓ |

**User's choice:** Nemotron 3 Super
**Notes:** Plan 02 verifies; fallback `nvidia/nemotron-4-340b-instruct`.

### Q2c - Why-it-matters model

| Option | Description | Selected |
|--------|-------------|----------|
| Claude Sonnet 4.6 (recommended) | Synthesis + reasoning. | |
| Claude Opus 4.7 | Strongest synthesis, 5× cost. | |
| Gemini 2.5 Pro | Competitive on synthesis. | |
| (Free text) | GPT-5.4 | ✓ |

**User's choice:** GPT-5.4
**Notes:** Plan 02 verifies; fallback `openai/gpt-5`.

### Q2d - Embedding model

| Option | Description | Selected |
|--------|-------------|----------|
| Cohere embed-multilingual-v3.0 (recommended) | 1024-dim, widely used. | ✓ |
| Voyage embed-3 | 1024-dim, recent. | |
| OpenAI text-embedding-3-large | 3072-dim, very strong. | |

**User's choice:** Cohere embed-multilingual-v3.0
**Notes:** Drives D-16.

---

## Config folder naming & MicroClaw relocation

### Q1 - Single config folder name + relocate `microclaw.config.yaml`?

| Option | Description | Selected |
|--------|-------------|----------|
| `config/` - relocate microclaw.config too | Closes F3 cleanup. Plan 02 verifies new path. | ✓ |
| `config/` - leave microclaw at repo root | Violates single-folder principle. | |
| `configs/` (plural) - relocate microclaw | Pure naming variant. | |
| Custom name | User-specified. | |

**User's choice:** `config/` - relocate microclaw.config too
**Notes:** Drives D-19.

---

## Per-task model selection timing

### Q1 - When do you pick the model per task?

| Option | Description | Selected |
|--------|-------------|----------|
| Right now - I propose, you approve | Starters finalized in THIS discussion. | ✓ |
| Before Plan 02 runs | Plan 02 first creates `config/models.yaml`; user edits. | |
| During Plan 02 execution | Interactive prompt per task. | |
| After Plan 02 - pick based on data | Plan 02 tests candidates; user picks winners. | |

**User's choice:** Right now - I propose, you approve
**Notes:** Led into Q2a–Q2d starter approval subquestions above.

---

## Update-Session Claude's Discretion

- OpenRouter Python client approach (raw `httpx` vs OpenRouter's official SDK).
- Retry / rate-limit / timeout defaults for OpenRouter HTTP client.
- YAML loader library (PyYAML vs ruamel.yaml).
- Model IDs for future task types not explicitly specified by user.

## Update-Session Deferred Ideas

- Control panel model-selection UI (Phase 2+ control panel).
- DM-based bot-receiver flow as @-mention alternative.
- Prefix-based or channel-whitelisted MicroClaw routing (alternative contract).
- STACK.md rewrite to reflect OpenRouter-only baseline.
- Relocation of `microclaw.config.yaml` to `config/` (scheduled within Plan 00-02 setup).
