<!-- GSD:project-start source:PROJECT.md -->
## Project

**Personal Agent Hub**

Personal Agent Hub is a personal AI-agent system for non-coding personal and business work. It is meant to monitor AI developments, surface useful resources, generate post ideas, and support future research workflows; v1 starts with a Discord-delivered daily AI news feed that filters the highest-signal updates about new models, notable product changes in tools like Claude Code and Cursor, interesting new AI tools, and hot trends.

**Core Value:** Deliver a high-signal, low-noise AI intelligence feed early enough to be useful, instead of making the user hunt through repetitive posts after everyone else has already amplified them.

### Constraints

- **Platform**: Windows-first foundation around MicroClaw and Ollama — existing architecture work already assumes this stack.
- **Delivery**: Discord-first for v1 — the digest must arrive where the user already wants to consume it.
- **Audience**: Single-user initial release — no v1 need for shared roles, permissions, or client-facing behavior.
- **Signal Quality**: Relevance and deduplication matter more than raw coverage — reducing noise is a success condition, not a nice-to-have.
- **Architecture**: Major handoffs must stay visible in chat and auditable in the control panel — trust and debugging depend on this.
- **Scope**: Prove one end-to-end workflow before expanding worker taxonomy or channel coverage — avoid overbuilding the full architecture upfront.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Bottom-line Recommendation
- **MicroClaw** as the Windows-first agent runtime and control plane
- **Ollama** as the local LLM + embeddings runtime
- **SQLite + sqlite-vec** as the only database for v1
- **Python 3.12 + uv** for ingestion/enrichment sidecars and custom MCP utilities
- **RSS/API-first ingestion** using `feedparser`, `httpx`, and `trafilatura`
- **Apify MCP** only as a fallback for sources that do not expose feeds or clean pages
- **Discord delivery through MicroClaw's native channel support**, not a separate bot framework by default
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
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Runtime | **MicroClaw** | LangGraph / CrewAI / Autogen-style orchestration | For this project they duplicate orchestration, add indirection, and weaken the "visible routing + control panel + Discord-first" fit. Use only if you abandon MicroClaw entirely. |
| Database | **SQLite + sqlite-vec** | PostgreSQL + pgvector | Good later for multi-user, remote access, or heavy concurrency. Premature for a single-user Windows-first v1. |
| Scraping | **RSS/API first + Apify fallback** | Playwright-first scraping | Browser-first ingestion is slower, more brittle, and harder to maintain. Use only for targeted exceptions. |
| Scheduling | **MicroClaw built-in scheduler** | Airflow / Temporal / Celery beat | Massive overkill for one daily digest workflow. |
| Discord delivery | **MicroClaw native Discord** | Standalone discord.py bot architecture | Only worth it if you need rich custom interaction patterns that MicroClaw cannot provide. Don't split delivery from orchestration on day 1. |
## Installation
# MicroClaw
# Build with semantic memory support enabled
# Python sidecars / utilities
# Optional only if you later need a custom Discord sidecar
# Optional fallback scraper MCP
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
- Stay on **SQLite + sqlite-vec**
- Keep **MicroClaw as the only runtime**
- Use **RSS/API-first ingestion**
- Because the real bottleneck is signal quality, not infrastructure scale
- Add **Apify MCP** for targeted hard sources
- Add **YouTube transcript ingestion** for a tiny allowlist
- Because coverage gaps should be solved with better source adapters, not a bigger core stack
- Keep **Ollama** for triage/dedup/embeddings
- Add a **remote provider only for final synthesis**, behind MicroClaw's provider layer
- Because quality upgrades should be isolated to the final-writing step, not force a full architecture change
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
- **MicroClaw v0.1.50**
- **Ollama v0.20.5**
- **SQLite + sqlite-vec v0.1.9**
- **Python 3.12 + uv 0.11.6**
- **feedparser + httpx + trafilatura + pydantic + rapidfuzz**
- **Apify MCP only as fallback**
- **Discord via MicroClaw native integration**
## Sources
- MicroClaw GitHub / README - https://github.com/microclaw/microclaw  
- MicroClaw release v0.1.50 - https://github.com/microclaw/microclaw/releases/tag/v0.1.50  
- Ollama API docs - https://github.com/ollama/ollama/blob/main/docs/api.md  
- Ollama release v0.20.5 - https://github.com/ollama/ollama/releases/tag/v0.20.5  
- sqlite-vec - https://github.com/asg017/sqlite-vec  
- sqlite-vec release v0.1.9 - https://github.com/asg017/sqlite-vec/releases/tag/v0.1.9  
- Apify MCP Server - https://github.com/apify/apify-mcp-server  
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.github/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
