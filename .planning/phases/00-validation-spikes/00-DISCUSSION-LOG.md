# Phase 0: Validation Spikes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

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
**Notes:** More objective than manual recall — uses real feed data.

---

| Option | Description | Selected |
|--------|-------------|----------|
| 70% coverage | If 9 feeds catch at least 70% of important AI news, watchlist is good enough | |
| 50% coverage | Lower bar — just needs to prove it catches something useful | ✓ |
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
**Notes:** Watchlist is non-blocking — easy to expand later.

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
| ~32B parameter range | Qwen3-Coder:32B, Gemma 4:27B — good quality/resource balance | ✓ |
| ~8B parameter range | Llama 3.1:8B, Qwen3:8B — faster but lower quality ceiling | |
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
**Notes:** Efficient — don't over-invest in model comparison.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Separate embedding model | Dedicated small model (nomic-embed-text, mxbai-embed-large) for sqlite-vec | ✓ |
| Same model for everything | Use 32B model's embedding endpoint for both tasks | |
| You decide | Claude picks embedding model | |

**User's choice:** Separate embedding model
**Notes:** Standard practice — embedding models are specialized.

---

## Claude's Discretion

- Specific first-choice ~32B Ollama model selection
- Specific embedding model selection

## Deferred Ideas

None — discussion stayed within phase scope.

## Folded Todos

All three matched todos were folded into Phase 0 scope:
- Set up MicroClaw + Ollama prototype → MicroClaw spike core
- Prototype MicroClaw visible-routing layer → MicroClaw spike stretch goal
- Rescope v1 around one visible workflow → synthesis output after all spikes
