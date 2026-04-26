# Phase 0: Validation Spikes - Research

**Researched:** 2026-04-13
**Updated:** 2026-04-24 (OpenRouter pivot; Plan 00-01 complete; Spike 2 rewritten)
**Domain:** MicroClaw runtime validation (COMPLETE), OpenRouter model quality evaluation, RSS watchlist backtesting
**Confidence:** MEDIUM-HIGH

## Summary

Phase 0 consists of three sequential validation spikes that convert key project assumptions (R1, R3, R4) into evidence before committing to Phase 1 implementation.

**Spike 1 (MicroClaw):** COMPLETE as of 2026-04-23. All 4 capabilities confirmed on Windows 11 x86_64. R1 CLOSED. Key finding: @-mention required for inbound flows (F1, locked as D-23). Machine has 32 GB RAM, ~6.4 GB free at baseline. No GPU offload viable (AMD Radeon 890M, 512 MB VRAM).

**Spike 2 (LLM model quality):** PIVOTED 2026-04-24 from local Ollama to OpenRouter. 32B local inference is not viable with 6.4 GB free RAM and no GPU offload. Plan 00-02 must be rewritten to evaluate OpenRouter-hosted models (D-13 through D-22). Uses `httpx` to hit OpenRouter's OpenAI-compatible endpoints. Models are per-task and config-driven (D-15, D-17). Starter assignments in D-18 must be verified against `/v1/models` before running evaluation.

**Spike 3 (Watchlist backtest):** Still pending. Automated Python feed scan using feedparser + httpx. Pass if >= 50% coverage of important AI news from the past week.

**Primary recommendation:** Rewrite Plan 00-02 around OpenRouter before executing. Use `httpx` directly (no SDK needed). Load API key from `config/microclaw.config.yaml`. Verify D-18 model IDs against `/v1/models` as the first task step. For Spike 3, use the feedparser script structure from the original research.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Spike Scope & Pass/Fail Criteria
- **D-01:** MicroClaw spike smoke test - 4 capabilities on Windows. **COMPLETE 2026-04-23: all 4 PASS.**
- **D-02:** LLM model-quality spike - run 10-15 representative tasks (ranking, summarization, "why it matters"). Pass/fail by user judgment. **Reinterpreted 2026-04-24 per D-13 to target OpenRouter-hosted models.**
- **D-03:** Watchlist spike - fetch 9 feeds, list items, user reviews. Pass = catches >= 50% of important AI news from past week.

#### Fallback Strategy
- **D-04:** MicroClaw fallback to NanoClaw on WSL2. **MOOT: MicroClaw GO 2026-04-23.**
- **D-05:** SUPERSEDED by D-13. Remote-only via OpenRouter is the baseline, not a fallback.
- **D-06:** If watchlist coverage < 50%, accept and move on. Don't block Phase 1.

#### LLM Provider & Model Selection (revised 2026-04-24)
- **D-13:** Remote-only for all LLM tasks via OpenRouter. No local Ollama chat path.
- **D-14:** OpenRouter is the sole LLM provider. No direct Anthropic/OpenAI/Google/Cohere API clients elsewhere.
- **D-15:** Per-task model selection. Each task type has its own model assignment, independently tunable.
- **D-16:** Embedding starter: `cohere/embed-multilingual-v3.0` (1024-dim). If unavailable on OpenRouter, fallback order: `voyage-3` → `openai/text-embedding-3-large`.
- **D-17:** Model configuration externalized to `config/models.yaml`. No hardcoded model IDs in application code.
- **D-18:** Starter model assignments (Plan 00-02 must verify each against `/v1/models`):
  - `ranking` → **Gemini 3 Flash Preview**
  - `summarization` → **Nemotron 3 Super**
  - `why_it_matters` → **GPT-5.4**
  - `embedding` → **cohere/embed-multilingual-v3.0**

#### Configuration & Secrets Layout
- **D-19:** Single `config/` folder at repo root. `microclaw.config.yaml` moves from repo root to `config/microclaw.config.yaml`. `models.yaml` alongside. Whole folder gitignored.
- **D-20:** OpenRouter API key stored inside `config/microclaw.config.yaml` alongside Discord bot token. Already gitignored.
- **D-21:** `config/models.yaml` minimum schema: `tasks: { ranking, summarization, why_it_matters, embedding }` each with `model: "<openrouter-id>"`.

#### Plan 00-02 Budget & Safety
- **D-22:** $20 hard cap on Plan 00-02 OpenRouter spend. Expected actual: ~$0.30 for single-pass 15-task eval.

#### MicroClaw Runtime Contracts (from Plan 00-01)
- **D-23:** @-mention is the locked contract for MicroClaw inbound Discord flows. Phase 1 is outbound-only (D-24), so F1 doesn't block Phase 1.
- **D-24:** Phase 1 scope is daily digest outbound-only.

### Claude's Discretion
- Claude picks retry/rate-limit/timeout defaults for the OpenRouter httpx client.
- Claude picks YAML loader library (PyYAML confirmed in STACK.md).
- Claude proposes model IDs for any task type added beyond D-18.

### Deferred Ideas (OUT OF SCOPE for Phase 0)
- Control panel model-selection UI (Phase 2+ control panel)
- DM-based bot-receiver flow (revisit if @-mention UX proves friction-heavy)
- STACK.md rewrite to fully reflect OpenRouter baseline (small follow-up)

</user_constraints>

## Standard Stack

### Core (Spike Dependencies)

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **MicroClaw** | **v0.1.50** (installed) | Runtime - VALIDATED Plan 00-01 | HIGH - verified locally |
| **OpenRouter** | API (no SDK) | Single LLM provider for chat + embeddings | HIGH - docs verified |
| **Python** | **3.12.x** (target; 3.13.12 installed) | OpenRouter client script + watchlist backtest | HIGH - installed |
| **uv** | **0.8.13** (installed; 0.11.6 target) | Python environment management for spike scripts | HIGH - installed |
| **httpx** | **0.28.1** | OpenRouter API client (chat + embeddings) | HIGH - standard async HTTP |
| **feedparser** | **6.0.12** | RSS/Atom feed parsing for watchlist spike | HIGH - standard |
| **PyYAML** | **6.0.2+** | Load `config/models.yaml` | HIGH - confirmed in STACK.md |
| **pydantic** | **2.12.5** | Typed schema for model config loader | HIGH - confirmed in STACK.md |

### OpenRouter Verified Model IDs

Researched 2026-04-24. Verify against `/v1/models` at Plan 00-02 execution — IDs may shift.

| Task | D-18 Starter Name | Likely OpenRouter ID | Fallback ID | Confidence |
|------|-------------------|---------------------|-------------|------------|
| `ranking` | Gemini 3 Flash Preview | `google/gemini-3-flash-preview` | `google/gemini-2.5-flash` | HIGH |
| `summarization` | Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b` (`:free` variant exists) | `nvidia/nemotron-4-340b-instruct` | HIGH |
| `why_it_matters` | GPT-5.4 | `openai/gpt-5.4` | `openai/gpt-5` | HIGH |
| `embedding` | cohere/embed-multilingual-v3.0 | `cohere/embed-multilingual-v3.0` | `voyage-3` → `openai/text-embedding-3-large` | LOW - availability on OpenRouter `/v1/embeddings` unconfirmed |

**Critical note on embedding:** `cohere/embed-multilingual-v3.0` availability through OpenRouter's `/v1/embeddings` endpoint is NOT confirmed. Research found OpenRouter lists Cohere Command and Rerank models, but embedding-specific availability is unclear. The Plan 00-02 step to verify `/v1/models` is load-bearing for this model. If absent, the fallback chain per D-16 applies: `voyage-3` → `openai/text-embedding-3-large`.

**Critical note on Nemotron:** The free tier uses `nvidia/nemotron-3-super-120b-a12b:free`. If rate limits are too restrictive on the free tier during the 15-task eval, use the paid variant (drop `:free` suffix).

## Architecture Patterns

### Spike 1: MicroClaw Validation — COMPLETE

**Result:** GO. All 4 tests PASS. See `00-01-SPIKE-RESULTS.md` for full details.

**Key contracts established:**
- @-mention required for inbound Discord flows (F1, D-23)
- Scheduler poll interval ~60 seconds
- SQLite DB at `C:\Users\galzi\.microclaw\runtime\microclaw.db`
- Web control panel at `http://127.0.0.1:10961`
- Config at `./microclaw.config.yaml` (repo root; relocating to `config/` per D-19)

---

### Spike 2: OpenRouter Model Quality Evaluation

**What Plan 00-02 must do:**

1. **Setup** — Relocate `microclaw.config.yaml` to `config/microclaw.config.yaml` (D-19). Add OpenRouter API key to it (D-20). Create `config/models.yaml` with D-18 starters (D-21).

2. **Verify model availability** — Call `GET https://openrouter.ai/api/v1/models` with bearer auth. Confirm each D-18 starter ID is present. Log "alt-picked" finding for any that requires fallback.

3. **Run evaluation** — 10-15 tasks across ranking, summarization, why_it_matters using httpx against `/v1/chat/completions`. Record output + latency for each.

4. **Verify embedding** — Test `/v1/embeddings` with the embedding model. Confirm it returns a vector; note dimensionality.

5. **Pass/fail judgment** — User reviews outputs. Majority usable = PASS.

**OpenRouter API pattern:**

```python
import httpx
import yaml
import time

# Load config
with open("config/microclaw.config.yaml") as f:
    cfg = yaml.safe_load(f)
OPENROUTER_KEY = cfg["openrouter_api_key"]

BASE_URL = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",   # required by OpenRouter
    "X-Title": "Personal Agent Hub Spike",
}

def chat(model: str, prompt: str) -> tuple[str, float]:
    start = time.monotonic()
    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=60,
    )
    resp.raise_for_status()
    elapsed = time.monotonic() - start
    return resp.json()["choices"][0]["message"]["content"], elapsed

def embed(model: str, text: str) -> list[float]:
    resp = httpx.post(
        f"{BASE_URL}/embeddings",
        headers=HEADERS,
        json={"model": model, "input": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]

def verify_models(required_ids: list[str]) -> dict[str, bool]:
    resp = httpx.get(f"{BASE_URL}/models", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    available = {m["id"] for m in resp.json()["data"]}
    return {mid: mid in available for mid in required_ids}
```
[VERIFIED: OpenRouter API docs — `/v1/chat/completions` (OpenAI-compatible), `/v1/embeddings`, bearer auth, `HTTP-Referer` required]

**`config/models.yaml` schema (D-21):**

```yaml
tasks:
  ranking:        { model: "google/gemini-3-flash-preview" }
  summarization:  { model: "nvidia/nemotron-3-super-120b-a12b" }
  why_it_matters: { model: "openai/gpt-5.4" }
  embedding:      { model: "cohere/embed-multilingual-v3.0" }
```

**Evaluation prompt templates:**

```python
RANKING_PROMPT = """Given these {n} AI news items, rank them by importance for someone who builds AI-powered tools.
Reply with the ranked list (1=most important) and one sentence of rationale per item.

{items}"""

SUMMARIZATION_PROMPT = """Summarize this AI news item in 2-3 sentences for a developer audience:

{article}"""

WHY_IT_MATTERS_PROMPT = """Explain in 2 sentences why this matters for someone who builds with AI tools:

{headline}

{first_paragraph}"""
```

**Test corpus (use real recent AI news items):**
- 5 ranking tasks (3-5 items each, use real headlines from the past week)
- 5 summarization tasks (paste real article snippets)
- 3-5 why_it_matters tasks (real headlines + first paragraph)

**Cost guardrail (D-22):**
```python
# OpenRouter returns usage in response
total_cost_usd = 0.0
SPEND_CAP = 18.0  # abort at $18, hard cap $20 per D-22

# After each call, add to total_cost_usd via usage.prompt_tokens + completion_tokens * per-model rate
# Log cumulative cost; abort spike if cap approaches
```
[ASSUMED: cost tracking via OpenRouter usage field in response; actual per-token rates vary by model]

---

### Spike 3: Watchlist Backtest

**The 9 starter feeds** (from RISK-REVIEW.md A3):
1. OpenAI blog
2. Google DeepMind blog
3. Cursor changelog/blog
4. Claude Code / Anthropic blog
5. VS Code Copilot updates
6. Ollama releases (GitHub releases.atom)
7. TestingCatalog
8. Simon Willison's blog
9. Latent Space podcast/blog

**Approach:** Fetch all 9 feeds NOW, filter to past 7 days, present list for manual user review. Pass if >= 50% coverage (D-03).

**Script structure:**
```python
# spike_watchlist.py
import feedparser
from datetime import datetime, timedelta

FEEDS = {
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "DeepMind Blog": "https://deepmind.google/blog/rss.xml",
    "Cursor Changelog": "https://changelog.cursor.com/feed.xml",
    "Anthropic Blog": "https://www.anthropic.com/rss.xml",
    "VS Code Copilot": "https://code.visualstudio.com/blogs/feed.xml",
    "Ollama Releases": "https://github.com/ollama/ollama/releases.atom",
    "TestingCatalog": "https://testingcatalog.com/rss.xml",
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Latent Space": "https://www.latent.space/feed",
}
# NOTE: URLs above are best-guess — MUST be verified during execution.

cutoff = datetime.now() - timedelta(days=7)
```
[VERIFIED: feedparser standard usage pattern]

**Important caveat:** RSS feeds are point-in-time snapshots. Items older than the feed's retention window will be missed. This is a known limitation — wrong URLs are data, not blockers.

## Anti-Patterns to Avoid

- **Using an OpenRouter Python SDK when httpx is sufficient** — OpenRouter's API is OpenAI-compatible; `httpx` + raw JSON is all that's needed for the spike. No LangChain, no `openai` SDK, no `anthropic` SDK.
- **Hardcoding model IDs in spike scripts** — Load from `config/models.yaml` from the start. Every script that hardcodes a model ID is a regression against D-17.
- **Testing too many models** — Per D-15, each task has one starter + one fallback. Don't evaluate 5 models per task; verify the starter works and fall back if it doesn't.
- **Skipping model availability check** — The `/v1/models` verification step is mandatory (especially for Cohere embedding). The fallback chain exists precisely because model IDs aren't guaranteed at execution time.
- **Building infrastructure during validation** — Spike scripts are disposable. No project structure, no CI, no tests during Phase 0.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenRouter API wrapper | Custom async OpenRouter client | `httpx` with raw JSON | The full spike needs ~30 lines of httpx; no SDK overhead |
| YAML config loading | Custom parser | `PyYAML safe_load` | Standard, already in STACK.md |
| Model ID verification | Assume IDs are correct | Call `/v1/models` first | Stale IDs cause confusing 404s; verify once, log findings |
| RSS parsing | Custom XML parser | feedparser 6.0.12 | Handles all RSS/Atom variants and their quirks |

## Common Pitfalls

### Pitfall 1: `HTTP-Referer` Header Missing
**What goes wrong:** OpenRouter returns 400 or 403 with a message about missing Referer header.
**Why it happens:** OpenRouter requires `HTTP-Referer` and optionally `X-Title` headers per their API docs — unlike a plain OpenAI endpoint.
**How to avoid:** Always include both headers. `HTTP-Referer: http://localhost` is acceptable for local dev/spike use.
**Warning signs:** 400 response with `missing required header` or similar.

### Pitfall 2: Cohere Embedding Model Unavailable on OpenRouter `/v1/embeddings`
**What goes wrong:** `/v1/models` lists the model but `/v1/embeddings` returns a 404 or model-not-found.
**Why it happens:** OpenRouter's embedding endpoint may not expose all embedding-capable models that appear in the chat models list. Cohere embed availability is LOW-confidence (see model table above).
**How to avoid:** Test the embedding endpoint explicitly in Step 1 of the eval (not just `/v1/models`). If it fails, immediately fall back to `voyage-3` per D-16. Record as a finding in MODEL-EVALUATION-RESULTS.md.
**Warning signs:** 404 on `/v1/embeddings`, or response with no `data[0].embedding` field.

### Pitfall 3: Nemotron Free Tier Rate Limits
**What goes wrong:** The `:free` variant of Nemotron hits rate limits during the 15-task evaluation, causing delays or failures.
**Why it happens:** Free-tier models on OpenRouter have lower rate limits than paid variants.
**How to avoid:** If rate limit errors appear, drop `:free` suffix to use the paid tier (covered by D-22 $20 cap). Expected actual cost for 15 tasks is ~$0.30.
**Warning signs:** 429 responses, unusually long delays.

### Pitfall 4: Config File Not at Expected Path After Relocation
**What goes wrong:** After relocating `microclaw.config.yaml` from repo root to `config/`, MicroClaw fails to start because it still looks for the old path.
**Why it happens:** MicroClaw may use a default config path that can only be overridden with a CLI flag.
**How to avoid:** Verify MicroClaw supports `--config ./config/microclaw.config.yaml` (or equivalent flag) before deleting the old path. Keep both until confirmed.
**Warning signs:** MicroClaw errors about missing config or Discord adapter failing to connect.

### Pitfall 5: RSS Feed URLs Wrong or Changed
**What goes wrong:** Feed URLs in the watchlist script return 404 or HTML, not XML.
**Why it happens:** Feed URLs aren't stable. The starter list was researched weeks ago.
**How to avoid:** First step of the watchlist spike = verify each URL. Failed feeds are data points, not blockers.
**Warning signs:** feedparser returns empty entries, HTTP 4xx, or HTML content type.

### Pitfall 6: Spending Approaching $20 Cap
**What goes wrong:** Multi-model comparison after a starter fails drives cost toward the $20 cap (D-22).
**Why it happens:** If 2-3 starters fail and need fallback comparison, token costs multiply.
**How to avoid:** Log cumulative cost after each call. Abort spike if total approaches $18. Expected single-pass cost is ~$0.30 — the cap exists for a multi-model comparison scenario, not the happy path.

## Code Examples

### Verify Model Availability
```python
import httpx, yaml

with open("config/microclaw.config.yaml") as f:
    cfg = yaml.safe_load(f)

headers = {
    "Authorization": f"Bearer {cfg['openrouter_api_key']}",
    "HTTP-Referer": "http://localhost",
}

resp = httpx.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=15)
available = {m["id"] for m in resp.json()["data"]}

required = [
    "google/gemini-3-flash-preview",
    "nvidia/nemotron-3-super-120b-a12b",
    "openai/gpt-5.4",
    "cohere/embed-multilingual-v3.0",
]
for mid in required:
    status = "FOUND" if mid in available else "MISSING"
    print(f"  {status}: {mid}")
```

### Run a Ranking Task
```python
import time

def ranking_task(model: str, items: list[str]) -> tuple[str, float]:
    numbered = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    prompt = f"Rank these AI news items by importance for someone who builds AI-powered tools. Reply with the ranked list and one sentence rationale per item:\n\n{numbered}"
    start = time.monotonic()
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=60,
    )
    resp.raise_for_status()
    elapsed = time.monotonic() - start
    return resp.json()["choices"][0]["message"]["content"], elapsed
```

### Test Embedding Endpoint
```python
def test_embedding(model: str, text: str = "OpenAI released a new model") -> dict:
    resp = httpx.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers=headers,
        json={"model": model, "input": text},
        timeout=30,
    )
    if resp.status_code != 200:
        return {"status": "FAIL", "code": resp.status_code, "body": resp.text}
    data = resp.json()["data"][0]["embedding"]
    return {"status": "PASS", "dimensions": len(data), "sample": data[:5]}
```

## State of the Art

| Old Approach | Current Approach | Changed | Impact |
|--------------|------------------|---------|--------|
| Local Ollama (Qwen3 32B / Gemma 4 27B) | OpenRouter remote per-task models | 2026-04-24 | Major — all Phase 0 Spike 2 instructions referencing Ollama are superseded |
| Single model for all tasks | Per-task model selection via `config/models.yaml` | 2026-04-24 | Structural change — config-driven from day 1 |
| nomic-embed-text (local Ollama) | cohere/embed-multilingual-v3.0 via OpenRouter | 2026-04-24 | Availability unconfirmed; fallback chain documented |
| `microclaw.config.yaml` at repo root | `config/microclaw.config.yaml` (D-19) | 2026-04-24 (planned) | Setup step in Plan 00-02 |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Feed URLs for the 9 starter sources are approximately correct | Spike 3 | Low — verifying URLs is part of the spike |
| A2 | OpenRouter's `/v1/embeddings` endpoint accepts the same bearer auth and `HTTP-Referer` headers as `/v1/chat/completions` | OpenRouter API pattern | Low — same auth scheme per docs |
| A3 | `cohere/embed-multilingual-v3.0` returns 1024-dim vectors if available on OpenRouter | Embedding model | Medium — if dimensions differ, sqlite-vec schema needs updating |
| A4 | OpenRouter cost for 15 evaluation tasks is well under $20 | D-22 budget | Low — worst case multi-model comparison is still likely < $5 |
| A5 | MicroClaw accepts `--config ./config/microclaw.config.yaml` CLI flag for relocated config | Pitfall 4 | Medium — if not supported, D-19 relocation must wait for Phase 1 |
| A6 | `nvidia/nemotron-3-super-120b-a12b` (without `:free`) is available on paid tier if free tier rate limits trigger | Pitfall 3 | Low — paid variant historically available when free is listed |

## Open Questions

1. **Does `cohere/embed-multilingual-v3.0` actually work through OpenRouter's `/v1/embeddings` endpoint?**
   - What we know: Model appears in Cohere section of OpenRouter catalog; embedding endpoint exists per docs.
   - What's unclear: Whether this specific embedding model is exposed vs. only chat/completion models.
   - Recommendation: Test this in Step 1 of Plan 00-02 before running any evaluation. If fails, immediately use `voyage-3`.

2. **Does MicroClaw support a `--config` CLI flag for non-default config paths?**
   - What we know: Config currently lives at repo root, which works. D-19 calls for relocation to `config/`.
   - What's unclear: Whether MicroClaw reads config via a flag or a fixed convention.
   - Recommendation: Check `microclaw --help` output. If no flag, defer D-19 relocation to Phase 1 and only create `config/models.yaml` in Plan 00-02.

3. **Are the exact Nemotron and Gemini model IDs correct?**
   - What we know: Research found `google/gemini-3-flash-preview` and `nvidia/nemotron-3-super-120b-a12b` as likely IDs (HIGH confidence).
   - What's unclear: Whether the Gemini variant should include a date suffix (e.g., `-20251217`).
   - Recommendation: Check `/v1/models` endpoint at execution time and use the exact ID from the response.

## Environment Availability

| Dependency | Required By | Available | Version | Notes |
|------------|-------------|-----------|---------|-------|
| MicroClaw | Phase 1+ | YES | v0.1.50 | Validated Plan 00-01 |
| OpenRouter API key | Spike 2 | NEEDS SETUP | -- | Add to `config/microclaw.config.yaml` |
| Python | Spikes 2 & 3 | YES | 3.13.12 | 3.12 preferred for compatibility; 3.13 functional |
| uv | Spikes 2 & 3 | YES | 0.8.13 | Functional for spike; 0.11.6 is STACK.md target |
| httpx | Spike 2 | NEEDS INSTALL | 0.28.1 | `uv pip install httpx==0.28.1` |
| PyYAML | Spike 2 | NEEDS INSTALL | 6.0.2+ | `uv pip install PyYAML` |
| feedparser | Spike 3 | NEEDS INSTALL | 6.0.12 | `uv pip install feedparser==6.0.12` |
| System RAM | Spike 2 (irrelevant now) | YES | ~32 GB | Confirmed Plan 00-01; irrelevant for remote LLM |
| GPU | Spike 2 (irrelevant now) | AMD Radeon 890M | 512 MB VRAM | No useful offload; moot with OpenRouter |
| Ollama | NOT NEEDED for Spike 2 | Running (0.21.0) | -- | Not used by Plan 00-02; keep for potential future use |

**Missing with no fallback:** OpenRouter API key — must be obtained from openrouter.ai before Plan 00-02 can run.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual validation (spikes are smoke tests) |
| Automation | Partially automated (Python scripts) |
| Config file | `config/models.yaml` (Plan 00-02 output) |
| Quick run | `python spike_openrouter.py` |

### Spike → Requirement Map

| Spike | Behavior | Validation Method | Automated? |
|-------|----------|-------------------|------------|
| MicroClaw | All 4 capabilities | Manual smoke test | No — COMPLETE |
| OpenRouter | Model availability | `/v1/models` API call | Yes |
| OpenRouter | Ranking quality | 5 tasks, user judges | Partial |
| OpenRouter | Summarization quality | 5 tasks, user judges | Partial |
| OpenRouter | Why-it-matters quality | 3-5 tasks, user judges | Partial |
| OpenRouter | Embedding endpoint works | `/v1/embeddings` test call | Yes |
| Watchlist | Feeds return recent items | Python feedparser script | Partial |
| Watchlist | Coverage >= 50% | User review | No |

## Security Domain

| ASVS Category | Applies | Notes |
|---------------|---------|-------|
| V2 Authentication | No | No app auth in spikes |
| V6 Cryptography | Minimal | OpenRouter API key — store in gitignored `config/microclaw.config.yaml` only |

**Sole security note:** OpenRouter API key must never be committed to git. `config/microclaw.config.yaml` is already gitignored (commit `10eb975`). The new `config/models.yaml` is safe to track (no secrets; only model IDs). Use granular `.gitignore` entries if the full `config/` folder is not blanket-ignored.

## Sources

### Primary (HIGH confidence)
- [OpenRouter API docs](https://openrouter.ai/docs) — verified `/v1/chat/completions`, `/v1/embeddings`, bearer auth, `HTTP-Referer` requirement, per-model pricing
- [OpenRouter models catalog](https://openrouter.ai/models) — verified model availability research
- [Plan 00-01 SPIKE-RESULTS.md](.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md) — environment facts: 32 GB RAM, 6.4 GB free, AMD Radeon 890M, MicroClaw validated
- [Phase 0 CONTEXT.md](.planning/phases/00-validation-spikes/00-CONTEXT.md) — D-13 through D-24 decisions locked 2026-04-24
- Local environment probes — Python 3.13.12, uv 0.8.13, Ollama 0.21.0, MicroClaw v0.1.50

### Secondary (MEDIUM confidence)
- [OpenRouter - Gemini 3 Flash Preview](https://openrouter.ai/google/gemini-3-flash-preview) — model ID confirmed
- [OpenRouter - Nemotron 3 Super](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free) — free variant confirmed; paid ID inferred
- [OpenRouter - GPT-5.4](https://openrouter.ai/openai/gpt-5.4) — model ID confirmed
- [OpenRouter Embeddings API](https://openrouter.ai/docs/api/reference/embeddings) — endpoint exists
- `.planning/research/STACK.md` — confirmed httpx, PyYAML, pydantic as standard choices

### Tertiary (LOW confidence)
- `cohere/embed-multilingual-v3.0` availability on OpenRouter `/v1/embeddings` — unconfirmed; must test at execution
- Feed URLs for 9 starter sources — best-guess, must verify during Spike 3

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — OpenRouter API verified, Python deps confirmed, environment known
- OpenRouter model IDs: HIGH for chat models; LOW for Cohere embedding availability
- Architecture (spike design): MEDIUM — OpenRouter client pattern is standard; config relocation (D-19) has one open question about MicroClaw's `--config` flag support
- Pitfalls: MEDIUM-HIGH — based on known OpenRouter behavior and D-19/D-20 config decisions

**Research dates:** Original 2026-04-13; updated 2026-04-24
**Valid until:** 2026-05-08 (2 weeks — model availability may shift; verify IDs at execution)
