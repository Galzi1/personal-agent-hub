# Technology Stack

**Project:** Personal Agent Hub
**Domain:** Discord-first personal AI-intel agent system
**Researched:** 2026-04-11
**Revised:** 2026-04-24 - OpenRouter pivot (supersedes local Ollama chat/embeddings baseline; see Phase 0 CONTEXT.md D-13 through D-22)
**Confidence:** MEDIUM-HIGH

## Recommended Stack

### Bottom-line Recommendation

For v1, the right stack is:

- **MicroClaw** as the Windows-first agent runtime and control plane *(validated 2026-04-23 - R1 CLOSED)*
- **OpenRouter** as the single LLM provider for chat (ranking, summarization, why-it-matters) and embeddings - per-task model selection, config-driven
- **SQLite + sqlite-vec** as the only database for v1
- **Python 3.12 + uv** for ingestion/enrichment sidecars, the OpenRouter client, and custom MCP utilities
- **RSS/API-first ingestion** using `feedparser`, `httpx`, and `trafilatura`
- **Apify MCP** only as a fallback for sources that do not expose feeds or clean pages
- **Discord delivery through MicroClaw's native channel support**, not a separate bot framework by default

That gives you the standard 2025-style agent stack shape for this category - chat-native runtime + MCP tools + lightweight local database + remote LLM layer - while staying aligned with the project's actual constraints: single user, Windows, secrets-local, visible routing, layered memory, and auditability.

**Why OpenRouter instead of local Ollama:** Plan 00-01 confirmed only ~6.4 GB free RAM at baseline on the target Windows 11 machine. A 32B-class local model needs ~20 GB resident plus headroom; GPU offload is not viable on the available AMD Radeon 890M (512 MB VRAM). OpenRouter provides unified billing, auth, and retry policy across the models the project actually wants for ranking / summarization / why-it-matters / embeddings - at a cost profile (~$0.30 expected for the full Phase 0 evaluation) that makes local sacrifice unnecessary.

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **MicroClaw** | **v0.1.50** | Core agent runtime, Discord delivery, scheduling, sub-agents, control panel | Validated 2026-04-23 on Windows 11 x86_64 (see `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md`). All 4 smoke tests PASS: scheduler, Discord outbound, SQLite persistence, control panel access. **Confidence: HIGH** |
| **OpenRouter** | API (no pinned SDK) | Single remote LLM provider for chat + embeddings via per-task model selection | Removes 32B-class local inference from the critical path. Unified auth and billing; single retry/rate-limit policy; portable model switching via config without code changes. **Confidence: HIGH** |
| **SQLite** | **3.45+ guidance** | Primary relational store for raw items, normalized items, clusters, digests, run history, memory metadata | For a single-user Windows-first system, SQLite is the standard "start here" choice: trivial ops, fast enough, easy backup, and fits MicroClaw natively. **Confidence: MEDIUM** |
| **sqlite-vec** | **v0.1.9** | Semantic retrieval and duplicate clustering using OpenRouter-sourced embeddings | Avoids introducing a separate vector database. Fits the local-first/single-user scope and matches MicroClaw's optional semantic-memory path. Stores vectors produced by `cohere/embed-multilingual-v3.0` (1024-dim) via OpenRouter. **Confidence: HIGH** |
| **Python** | **3.12.x** | Ingestion, normalization, extraction, ranking helpers, OpenRouter client, custom MCP servers | Python has the best practical ecosystem for feeds, content extraction, fuzzy matching, and quick MCP sidecars. Prefer 3.12 for smoother package compatibility on Windows. **Confidence: MEDIUM** |
| **uv** | **0.11.6** | Python environment/package management | Fastest and simplest way to manage Python sidecars reproducibly. Standard choice for greenfield Python tooling. **Confidence: HIGH** |

### LLM Task → Model Matrix

Per-task model selection is a first-class framework concern (Phase 0 D-15/D-17/D-18). Models are assigned in `config/models.yaml` and editable via the control panel in later phases. Hardcoding model IDs in application code is a regression.

**Starter assignments (to be verified against OpenRouter `/v1/models` at Plan 00-02 execution):**

| Task | Starter Model | Fallback if Unavailable | Rationale |
|------|---------------|-------------------------|-----------|
| `ranking` | **Gemini 3 Flash Preview** | `google/gemini-2.5-flash` | Cheap, fast, adequate for instruction-following on 3-10 item rankings |
| `summarization` | **Nemotron 3 Super** | `nvidia/nemotron-4-340b-instruct` | Strong on structured summaries; cheap via OpenRouter |
| `why_it_matters` | **GPT-5.4** | `openai/gpt-5` | Needs synthesis + contextual insight; small output (2 sentences) |
| `embedding` | **cohere/embed-multilingual-v3.0** | `voyage-3` → `openai/text-embedding-3-large` | 1024-dim, widely supported on OpenRouter, well-suited to sqlite-vec |

Final selection may change after Plan 00-02 results; models are swappable via config.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **feedparser** | **6.0.12** | RSS/Atom ingestion | Default source-ingestion layer for official blogs, changelogs, release feeds, and newsletters that expose feeds. **Use first.** **Confidence: HIGH** |
| **httpx** | **0.28.1** | Async HTTP client + OpenRouter API client | Use for source fetchers, page fetches, API polling, health checks, and the OpenRouter chat/embedding endpoints. Default client for all external HTTP. **Confidence: HIGH** |
| **trafilatura** | **2.0.0** | Main-article extraction from web pages | Use after source discovery to strip boilerplate and normalize article text before ranking/summarization. **Confidence: HIGH** |
| **pydantic** | **2.12.5** | Typed schemas for normalized items, digest cards, and the `config/models.yaml` loader | Use for every pipeline boundary: source item, canonical item, cluster, scored candidate, digest entry, handoff event. **Confidence: HIGH** |
| **PyYAML** | **6.0.2+** | Load `config/models.yaml` and `config/microclaw.config.yaml` | Standard choice for project YAML. Use `safe_load`. **Confidence: HIGH** |
| **rapidfuzz** | **3.14.5** | Fuzzy title matching and canonicalization | Use before embeddings to collapse obvious headline variants cheaply. **Confidence: HIGH** |
| **datasketch** | **1.9.0** | Near-duplicate detection on snippets/bodies | Use if simple title fuzziness is not enough; especially useful when many blogs reword the same launch. **Confidence: MEDIUM** |
| **mcp** | **1.27.0** | Custom MCP servers/tools | Use for project-specific ingestion, ranking, or memory-promotion utilities that should remain portable into MicroClaw. **Confidence: HIGH** |
| **@apify/actors-mcp-server** | **0.9.17** | Fallback scraper layer for hard sites | Use only when RSS/API/clean HTML fails. Official docs note the hosted MCP server has better features than local stdio. **Confidence: HIGH** |
| **youtube-transcript-api** | **1.2.4** | Transcript ingestion for key YouTube channels | Optional. Use only for a short allowlist of high-value channels; do not turn YouTube into the primary source class in v1. **Confidence: MEDIUM** |
| **discord.py** | **2.7.1** | Optional custom Discord sidecar | Only use if MicroClaw's native Discord support proves insufficient for embeds, buttons, or custom thread behavior. **Not a default dependency.** **Confidence: MEDIUM** |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Ruff** (`0.15.10`) | Linting/formatting for Python sidecars | Keep all helper services small and strict. |
| **Pytest** (`9.0.3`) | Regression tests for dedup/ranking logic | Especially important for title canonicalization and digest scoring. |
| **structlog** (`25.5.0`) | Structured application logs | Add if MicroClaw's built-in logs are not enough for sidecars. |
| **opentelemetry-sdk** (`1.41.0`) | Trace sidecars and enrichment steps | Optional for v1; useful once multiple workers exist. |

## Configuration Layout

Per Phase 0 D-19/D-20/D-21: **all YAML configuration lives in a single `config/` folder at repo root.**

```
config/
├── microclaw.config.yaml   # MicroClaw runtime config + Discord bot token + OpenRouter API key (gitignored)
└── models.yaml             # Per-task OpenRouter model selection (see schema below)
```

### `config/models.yaml` Schema

```yaml
tasks:
  ranking:        { model: "google/gemini-3-flash-preview" }
  summarization:  { model: "nvidia/nemotron-3-super" }
  why_it_matters: { model: "openai/gpt-5.4" }
  embedding:      { model: "cohere/embed-multilingual-v3.0" }
```

Optional per-task fields (temperature, max_tokens, top_p, timeout_s) allowed but not required. Python loader reads at startup; the future control panel edits via UI and writes the same file.

## Stack Shape for v1 Daily Digest

The actual v1 pipeline should look like this:

1. **Acquire**
   - Prefer **RSS/Atom**, official changelogs, GitHub releases, and clean public pages
2. **Extract**
   - Use `trafilatura` to turn pages into clean text
3. **Normalize**
   - Canonical URL, source, published time, product/entity tags
4. **Deduplicate**
   - First pass: exact URL + canonical URL + `rapidfuzz` title matching
   - Second pass: embeddings via OpenRouter (`cohere/embed-multilingual-v3.0`) stored in `sqlite-vec`
5. **Score**
   - Rule-based scoring first, OpenRouter model (`ranking` task) judgment second
6. **Synthesize**
   - Generate a concise daily digest with explicit source links; OpenRouter `summarization` + `why_it_matters` models produce the narrative
7. **Deliver**
   - Post to Discord through MicroClaw (outbound-only in Phase 1 per D-24)
8. **Persist**
   - Save raw items, clusters, digest output, and memory promotions in SQLite

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Runtime | **MicroClaw** | LangGraph / CrewAI / Autogen-style orchestration | For this project they duplicate orchestration, add indirection, and weaken the "visible routing + control panel + Discord-first" fit. Use only if you abandon MicroClaw entirely. |
| LLM Provider | **OpenRouter (single provider)** | Direct Anthropic / OpenAI / Google clients side-by-side | Multiple vendor SDKs fragment auth, retry logic, rate-limiting, and model swapping. OpenRouter is a thin layer that gives portability without multi-SDK overhead. |
| LLM Provider | **OpenRouter** | Local Ollama for all tasks | 32B local inference infeasible with 6.4 GB free RAM and no GPU offload on the target machine. Verified in Plan 00-01 environment capture. |
| LLM Provider | **OpenRouter** | Hybrid (local for some tasks, remote for others) | Per Phase 0 D-13: baseline is remote-only. Keeps the provider layer single-source. Revisit if privacy constraints shift later. |
| Database | **SQLite + sqlite-vec** | PostgreSQL + pgvector | Good later for multi-user, remote access, or heavy concurrency. Premature for a single-user Windows-first v1. |
| Scraping | **RSS/API first + Apify fallback** | Playwright-first scraping | Browser-first ingestion is slower, more brittle, and harder to maintain. Use only for targeted exceptions. |
| Scheduling | **MicroClaw built-in scheduler** | Airflow / Temporal / Celery beat | Massive overkill for one daily digest workflow. |
| Discord delivery | **MicroClaw native Discord** | Standalone discord.py bot architecture | Only worth it if you need rich custom interaction patterns that MicroClaw cannot provide. Don't split delivery from orchestration on day 1. |

## Installation

```bash
# MicroClaw (already installed and validated per Plan 00-01)
# Binary at C:\microclaw\microclaw
# Config: config/microclaw.config.yaml (after D-19 relocation)

# Python sidecars / utilities
uv python install 3.12
uv venv
uv pip install \
  feedparser==6.0.12 \
  httpx==0.28.1 \
  trafilatura==2.0.0 \
  pydantic==2.12.5 \
  PyYAML==6.0.2 \
  rapidfuzz==3.14.5 \
  datasketch==1.9.0 \
  mcp==1.27.0 \
  youtube-transcript-api==1.2.4 \
  ruff==0.15.10 \
  pytest==9.0.3 \
  structlog==25.5.0 \
  opentelemetry-sdk==1.41.0

# Optional only if you later need a custom Discord sidecar
uv pip install discord.py==2.7.1

# Optional fallback scraper MCP
npm install -g @apify/actors-mcp-server@0.9.17
```

OpenRouter requires no SDK install - use `httpx` directly against `https://openrouter.ai/api/v1/chat/completions` and `https://openrouter.ai/api/v1/embeddings`. API key loaded from `config/microclaw.config.yaml`.

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Pinecone / Weaviate / Qdrant as the initial vector store** | Extra infrastructure for no real v1 benefit. Single-user local-first does not need a network vector DB. | **SQLite + sqlite-vec** (with embeddings from OpenRouter) |
| **CrewAI / LangChain-first / agent-framework-first orchestration** | Duplicates MicroClaw's job, increases hidden routing, and makes the system harder to audit. | **MicroClaw + small typed sidecars/MCP tools** |
| **Playwright/Selenium scraping of LinkedIn or WhatsApp as a primary ingestion strategy** | Brittle, slow, noisy, and likely to become a maintenance sink. | **Official feeds, public pages, GitHub releases, curated allowlists, Apify only as fallback** |
| **Airflow / Temporal / Kafka / Redis / Celery** | Too much moving infrastructure for one scheduled digest. | **MicroClaw scheduler + SQLite-backed state** |
| **A separate React/Next.js control panel in v1** | You do not need a second app before proving signal quality. | **MicroClaw control plane + small targeted views later** |
| **One giant undifferentiated shared memory store** | Conflicts with the project's layered-memory direction and will pollute retrieval fast. | **Agent-local memory + smaller shared project memory with promotion rules** |
| **Direct Anthropic / OpenAI / Google SDKs side-by-side** | Fragments auth, retry logic, and rate-limiting; forces N-way model portability work. | **OpenRouter single provider** - swap models via `config/models.yaml` |
| **Hardcoded model IDs in Python source** | Defeats the "model config editable now, via control panel later" requirement (D-17). | **Load model IDs from `config/models.yaml`** |

## Stack Patterns by Variant

**If v1 stays single-user and remote-LLM first:** *(current posture)*
- Stay on **SQLite + sqlite-vec**
- Keep **MicroClaw as the only runtime**
- Use **RSS/API-first ingestion**
- Use **OpenRouter as the sole LLM provider** with per-task model selection in `config/models.yaml`
- Because the real bottleneck is signal quality, not infrastructure scale

**If digest quality is good but source coverage is weak:**
- Add **Apify MCP** for targeted hard sources
- Add **YouTube transcript ingestion** for a tiny allowlist
- Because coverage gaps should be solved with better source adapters, not a bigger core stack

**If an OpenRouter-hosted model is inadequate for a specific task:**
- Swap just that task's model in `config/models.yaml` - no code changes
- Try the fallback chain (e.g., `ranking` → fallback to a stronger Claude / Gemini tier)
- Because the config-driven model selection (D-17) exists precisely to absorb this variant

**If privacy constraints later demand local-only inference:**
- Reintroduce local Ollama only for tasks where local model quality is provably adequate
- Keep OpenRouter for tasks where it is not (hybrid variant)
- Consider a dedicated GPU host before committing to local-only
- Because the config-driven layer can route per-task without a full architecture change

**If the product later becomes multi-user or remote-first:**
- Move relational storage to **PostgreSQL + pgvector**
- Keep MCP boundaries so ingestion/ranking tools remain portable
- Because that is the point where SQLite convenience stops outweighing multi-user needs

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| **MicroClaw v0.1.50** | **OpenRouter via its generic OpenAI-compatible endpoint** | MicroClaw's LLM provider layer accepts an `openai`-style base URL; configure it to point at `https://openrouter.ai/api/v1`. Verified indirectly in Plan 00-01 (Anthropic config works via the same shape). |
| **MicroClaw v0.1.50** | **sqlite-vec enabled build** | Build with `--features sqlite-vec` if you want semantic KNN retrieval/dedup. |
| **MicroClaw MCP** | **stdio / streamable_http servers** | Current runtime supports `stdio` and `streamable_http`; SSE-only MCP servers need a bridge. |
| **Apify MCP hosted** | **MicroClaw MCP integration** | Official docs note hosted server has better features than local stdio. Prefer hosted for public-web scraping if acceptable. |
| **Discord delivery** | **MicroClaw native channel support** | MicroClaw handles long-message splitting. **Inbound contract:** channel messages must use `@<bot-name> <prompt>` format - plain text is silently dropped by the router (Plan 00-01 Finding F1, locked as D-23). |

## Recommendation Summary

**Use this stack:**

- **MicroClaw v0.1.50** *(validated)*
- **OpenRouter API** (per-task model selection via `config/models.yaml`)
- **SQLite + sqlite-vec v0.1.9**
- **Python 3.12 + uv 0.11.6**
- **feedparser + httpx + trafilatura + pydantic + PyYAML + rapidfuzz**
- **Apify MCP only as fallback**
- **Discord via MicroClaw native integration** (outbound-only in Phase 1 per D-24)

This is the right stack because it optimizes for the real v1 risk: **getting a trustworthy, deduplicated, high-signal digest out every day**, not building a flashy distributed agent platform too early - while sidestepping the infeasibility of 32B-class local inference on the target Windows machine.

## Sources

- MicroClaw GitHub / README - https://github.com/microclaw/microclaw
  - Verified: Discord support, scheduled tasks, sub-agents, control plane, MCP, sqlite-vec build path, OpenAI-compatible provider layer
- MicroClaw release v0.1.50 - https://github.com/microclaw/microclaw/releases/tag/v0.1.50
- OpenRouter API docs - https://openrouter.ai/docs
  - Verified: `/v1/chat/completions` (OpenAI-compatible), `/v1/embeddings`, per-model pricing, auth via `Authorization: Bearer <key>`
- OpenRouter models catalog - https://openrouter.ai/models
- sqlite-vec - https://github.com/asg017/sqlite-vec
- sqlite-vec release v0.1.9 - https://github.com/asg017/sqlite-vec/releases/tag/v0.1.9
- Apify MCP Server - https://github.com/apify/apify-mcp-server
  - Verified: hosted MCP recommendation and capability scope
- Apify MCP release v0.9.17 - https://github.com/apify/apify-mcp-server/releases/tag/v0.9.17
- PyPI: discord.py 2.7.1 - https://pypi.org/project/discord.py/
- PyPI: feedparser 6.0.12 - https://pypi.org/project/feedparser/
- PyPI: trafilatura 2.0.0 - https://pypi.org/project/trafilatura/
- PyPI: httpx 0.28.1 - https://pypi.org/project/httpx/
- PyPI: uv 0.11.6 - https://pypi.org/project/uv/
- PyPI: pydantic 2.12.5 - https://pypi.org/project/pydantic/
- PyPI: PyYAML 6.0.2 - https://pypi.org/project/PyYAML/
- PyPI: rapidfuzz 3.14.5 - https://pypi.org/project/rapidfuzz/
- PyPI: datasketch 1.9.0 - https://pypi.org/project/datasketch/
- PyPI: mcp 1.27.0 - https://pypi.org/project/mcp/
- PyPI: youtube-transcript-api 1.2.4 - https://pypi.org/project/youtube-transcript-api/
- PyPI: structlog 25.5.0 - https://pypi.org/project/structlog/
- PyPI: opentelemetry-sdk 1.41.0 - https://pypi.org/project/opentelemetry-sdk/
- Phase 0 validation spike results - `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md`, `.planning/phases/00-validation-spikes/00-CONTEXT.md`
