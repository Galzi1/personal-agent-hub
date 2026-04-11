# Technology Stack

**Project:** Personal Agent Hub  
**Domain:** Discord-first personal AI-intel agent system  
**Researched:** 2026-04-11  
**Confidence:** MEDIUM-HIGH

## Recommended Stack

### Bottom-line Recommendation

For v1, the right stack is:

- **MicroClaw** as the Windows-first agent runtime and control plane
- **Ollama** as the local LLM + embeddings runtime
- **SQLite + sqlite-vec** as the only database for v1
- **Python 3.12 + uv** for ingestion/enrichment sidecars and custom MCP utilities
- **RSS/API-first ingestion** using `feedparser`, `httpx`, and `trafilatura`
- **Apify MCP** only as a fallback for sources that do not expose feeds or clean pages
- **Discord delivery through MicroClaw's native channel support**, not a separate bot framework by default

That gives you the standard 2025-style agent stack shape for this category - chat-native runtime + MCP tools + lightweight local database + local model runtime - while staying aligned with this project's actual constraints: single user, Windows, local-first, visible routing, layered memory, and auditability.

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **MicroClaw** | **v0.1.50** | Core agent runtime, Discord delivery, scheduling, sub-agents, control panel | Best fit for the existing architecture direction. Official README verifies Discord support, scheduled tasks, MCP, local web control plane, SQLite persistence, sub-agent lifecycle, and Ollama support. **Use this as the runtime, not just as a wrapper.** **Confidence: HIGH** |
| **Ollama** | **v0.20.5** | Local chat model runtime and embeddings service | Official API docs verify `/api/chat`, tool calling, structured outputs, and `/api/embed`. This is the right local-first LLM layer for v1. **Confidence: HIGH** |
| **SQLite** | **3.45+ guidance** | Primary relational store for raw items, normalized items, clusters, digests, run history, memory metadata | For a single-user Windows-first system, SQLite is the standard "start here" choice: trivial ops, fast enough, easy backup, and fits MicroClaw natively. **Confidence: MEDIUM** |
| **sqlite-vec** | **v0.1.9** | Semantic retrieval and duplicate clustering | Avoids introducing a separate vector database. Fits the local-first/single-user scope and matches MicroClaw's optional semantic-memory path. **Confidence: HIGH** |
| **Python** | **3.12.x** | Ingestion, normalization, extraction, ranking helpers, custom MCP servers | Python has the best practical ecosystem for feeds, content extraction, fuzzy matching, and quick MCP sidecars. Prefer 3.12 for smoother package compatibility on Windows. **Confidence: MEDIUM** |
| **uv** | **0.11.6** | Python environment/package management | Fastest and simplest way to manage Python sidecars reproducibly. This is the standard choice now for greenfield Python tooling. **Confidence: HIGH** |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **feedparser** | **6.0.12** | RSS/Atom ingestion | Default source-ingestion layer for official blogs, changelogs, release feeds, and newsletters that expose feeds. **Use first.** **Confidence: HIGH** |
| **httpx** | **0.28.1** | Async HTTP client | Use for source fetchers, page fetches, API polling, and health checks. Better than ad-hoc requests code. **Confidence: HIGH** |
| **trafilatura** | **2.0.0** | Main-article extraction from web pages | Use after source discovery to strip boilerplate and normalize article text before ranking/summarization. **Confidence: HIGH** |
| **pydantic** | **2.12.5** | Typed schemas for normalized items and digest cards | Use for every pipeline boundary: source item, canonical item, cluster, scored candidate, digest entry, handoff event. **Confidence: HIGH** |
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
   - Second pass: embeddings in `sqlite-vec`
5. **Score**  
   - Rule-based scoring first, LLM judgment second
6. **Synthesize**  
   - Generate a concise daily digest with explicit source links and "why it matters"
7. **Deliver**  
   - Post to Discord through MicroClaw
8. **Persist**  
   - Save raw items, clusters, digest output, and memory promotions in SQLite

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Runtime | **MicroClaw** | LangGraph / CrewAI / Autogen-style orchestration | For this project they duplicate orchestration, add indirection, and weaken the "visible routing + control panel + Discord-first" fit. Use only if you abandon MicroClaw entirely. |
| Database | **SQLite + sqlite-vec** | PostgreSQL + pgvector | Good later for multi-user, remote access, or heavy concurrency. Premature for a single-user Windows-first v1. |
| Scraping | **RSS/API first + Apify fallback** | Playwright-first scraping | Browser-first ingestion is slower, more brittle, and harder to maintain. Use only for targeted exceptions. |
| Scheduling | **MicroClaw built-in scheduler** | Airflow / Temporal / Celery beat | Massive overkill for one daily digest workflow. |
| Discord delivery | **MicroClaw native Discord** | Standalone discord.py bot architecture | Only worth it if you need rich custom interaction patterns that MicroClaw cannot provide. Don't split delivery from orchestration on day 1. |

## Installation

```bash
# MicroClaw
# Build with semantic memory support enabled
cargo build --release --features sqlite-vec

# Python sidecars / utilities
uv python install 3.12
uv venv
uv pip install \
  feedparser==6.0.12 \
  httpx==0.28.1 \
  trafilatura==2.0.0 \
  pydantic==2.12.5 \
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

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Pinecone / Weaviate / Qdrant as the initial vector store** | Extra infrastructure for no real v1 benefit. Single-user local-first does not need a network vector DB. | **SQLite + sqlite-vec** |
| **CrewAI / LangChain-first / agent-framework-first orchestration** | Duplicates MicroClaw's job, increases hidden routing, and makes the system harder to audit. | **MicroClaw + small typed sidecars/MCP tools** |
| **Playwright/Selenium scraping of LinkedIn or WhatsApp as a primary ingestion strategy** | Brittle, slow, noisy, and likely to become a maintenance sink. Also poor fit for reliable daily production. | **Official feeds, public pages, GitHub releases, curated allowlists, Apify only as fallback** |
| **Airflow / Temporal / Kafka / Redis / Celery** | Too much moving infrastructure for one scheduled digest. | **MicroClaw scheduler + SQLite-backed state** |
| **A separate React/Next.js control panel in v1** | You do not need a second app before proving signal quality. | **MicroClaw control plane + small targeted views later** |
| **One giant undifferentiated shared memory store** | Conflicts with the project's layered-memory direction and will pollute retrieval fast. | **Agent-local memory + smaller shared project memory with promotion rules** |

## Stack Patterns by Variant

**If v1 stays single-user and local-first:**  
- Stay on **SQLite + sqlite-vec**
- Keep **MicroClaw as the only runtime**
- Use **RSS/API-first ingestion**
- Because the real bottleneck is signal quality, not infrastructure scale

**If digest quality is good but source coverage is weak:**  
- Add **Apify MCP** for targeted hard sources
- Add **YouTube transcript ingestion** for a tiny allowlist
- Because coverage gaps should be solved with better source adapters, not a bigger core stack

**If local models are not good enough for final digest writing:**  
- Keep **Ollama** for triage/dedup/embeddings
- Add a **remote provider only for final synthesis**, behind MicroClaw's provider layer
- Because quality upgrades should be isolated to the final-writing step, not force a full architecture change

**If the product later becomes multi-user or remote-first:**  
- Move relational storage to **PostgreSQL + pgvector**
- Keep MCP boundaries so ingestion/ranking tools remain portable
- Because that is the point where SQLite convenience stops outweighing multi-user needs

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| **MicroClaw v0.1.50** | **Ollama v0.20.x** | Official README verifies Ollama support; default Ollama base URL is `http://127.0.0.1:11434/v1`. |
| **MicroClaw v0.1.50** | **sqlite-vec enabled build** | Build with `--features sqlite-vec` if you want semantic KNN retrieval/dedup instead of keyword + Jaccard fallback. |
| **MicroClaw MCP** | **stdio / streamable_http servers** | Current runtime supports `stdio` and `streamable_http`; SSE-only MCP servers need a bridge. |
| **Apify MCP hosted** | **MicroClaw MCP integration** | Official docs note hosted server has better features than local stdio. Prefer hosted for public-web scraping if acceptable. |
| **Discord delivery** | **MicroClaw native channel support** | MicroClaw handles long-message splitting, which matters because Discord has strict message-size limits. |

## Recommendation Summary

**Use this stack:**

- **MicroClaw v0.1.50**
- **Ollama v0.20.5**
- **SQLite + sqlite-vec v0.1.9**
- **Python 3.12 + uv 0.11.6**
- **feedparser + httpx + trafilatura + pydantic + rapidfuzz**
- **Apify MCP only as fallback**
- **Discord via MicroClaw native integration**

This is the right stack because it optimizes for the real v1 risk: **getting a trustworthy, deduplicated, high-signal digest out every day**, not building a flashy distributed agent platform too early.

## Sources

- MicroClaw GitHub / README - https://github.com/microclaw/microclaw  
  - Verified: Discord support, scheduled tasks, sub-agents, control plane, MCP, sqlite-vec build path, Ollama support
- MicroClaw release v0.1.50 - https://github.com/microclaw/microclaw/releases/tag/v0.1.50  
- Ollama API docs - https://github.com/ollama/ollama/blob/main/docs/api.md  
  - Verified: `/api/chat`, tool calling, structured outputs, `/api/embed`
- Ollama release v0.20.5 - https://github.com/ollama/ollama/releases/tag/v0.20.5  
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
- PyPI: rapidfuzz 3.14.5 - https://pypi.org/project/rapidfuzz/  
- PyPI: datasketch 1.9.0 - https://pypi.org/project/datasketch/  
- PyPI: mcp 1.27.0 - https://pypi.org/project/mcp/  
- PyPI: youtube-transcript-api 1.2.4 - https://pypi.org/project/youtube-transcript-api/  
- PyPI: structlog 25.5.0 - https://pypi.org/project/structlog/  
- PyPI: opentelemetry-sdk 1.41.0 - https://pypi.org/project/opentelemetry-sdk/  
