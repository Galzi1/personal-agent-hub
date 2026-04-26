---
title: Architecture Repository Mapping
date: 2026-04-11
context: Exploration of which GitHub starred repositories best implement each component of the personal-agent-hub architecture
---

# Architecture → Repository Mapping

## Decision: MicroClaw as Foundation

**Chosen foundation:** [microclaw/microclaw](https://github.com/microclaw/microclaw) (Rust, 643⭐)

**Why MicroClaw over NanoClaw:**
- First-class Ollama provider (native, no proxy needed) — critical for the architecture's Ollama Runtime requirement
- Built-in web control plane at `:10961` — maps to Control Panel component
- sqlite-vec embeddings — maps to Vector Storage requirement
- Provider-agnostic (25 built-in providers including Ollama, OpenAI, Anthropic, Google, etc.)
- First-class sub-agent lifecycle (spawn/focus/kill) — maps to Worker Agents
- Native MCP support — all extensions wire in via standard protocol
- Native Windows support (PowerShell installer)

**Why not NanoClaw:**
- Claude Agent SDK dependency — Ollama is a sidekick, not a first-class provider
- Philosophically rejects dashboards ("ask Claude what's happening")
- No vector storage support
- Requires WSL2 on Windows

**Maturity risk mitigation:**
- Fork MicroClaw early, own the codebase
- Wire all integrations via MCP (portable protocol)
- Contribute back to upstream (small community = high impact)
- Keep NanoClaw as documented fallback path
- Docker image provides deployment insurance

---

## Component Mapping

### Access Layer (Discord · Slack · Telegram)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | Telegram, Discord, Slack, Feishu, IRC, Web UI, Matrix |

### Orchestrator Agent (Intent · Routes · Schedules)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | Shared agent loop, session state, plan & execute, cron + one-shot scheduling |

### Worker Agents (Resources · Ideas · News · Research · Digest)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | Sub-agent system (spawn/focus/kill) |
| MCP extension | `apify/apify-mcp-server` | Web scraping for News/Research workers |
| Extension | `HKUDS/LightRAG` | RAG engine for Research worker |
| Extension | `google/langextract` | Structured extraction for Digest worker |
| Reference | `lfnovo/open-notebook` | Ideas/knowledge notebook pattern |

### External Sources (Web · RSS · YouTube · News APIs)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | `web_search` + `web_fetch` tools |
| MCP extension | `apify/apify-mcp-server` | 1000+ scrapers for social media, news, search engines |

### Ollama Runtime (Gemma 4 · Embeddings)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | First-class Ollama provider, sqlite-vec embeddings |
| Infrastructure | `ollama/ollama` | Local LLM runtime |

### Storage (SQL · Vectors · Files)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | SQLite (SQL) + sqlite-vec (Vectors) + AGENTS.md (Files) |
| Scale option | `volcengine/OpenViking` | Context database if SQLite outgrown |

### Observability (Logs · Metrics · Context)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | Basic logging |
| Extension | `shmulikdav/LLMeter` | Per-feature, per-user LLM cost attribution |
| Extension | `hoodini/llm-visuals` | LLM visualization |

### Control Panel (Dashboard · Logs · Activity · Context)
| Source | Repository | Role |
|--------|-----------|------|
| **MicroClaw native** | `microclaw/microclaw` | Web UI at `:10961` |
| Enhancement | `saltbo/agent-kanban` (188⭐) | Agent-first task board overlay for multi-agent workforce visibility |

### Memory & Knowledge (Phase 4+)
| Source | Repository | Role |
|--------|-----------|------|
| Research candidate | `topoteretes/cognee` (15K⭐) | Knowledge engine for agent memory via knowledge graphs — potential upgrade from raw SQLite memory tables |
| Research candidate | `vectorize-io/hindsight` (9K⭐) | "Agent Memory That Learns" — aligns with feedback-driven memory promotion pattern in layered-memory-model.md |

---

## Cross-Cutting Repos

| Repository | Purpose |
|-----------|---------|
| `lasso-security/mcp-gateway` | Security gateway for MCP communications |
| `mksglu/context-mode` (7k⭐) | 98% context window reduction |
| `kunchenguid/axi` (679⭐) | Agent ergonomics, lower token costs |
| `rtk-ai/rtk` | CLI proxy, 60-90% token reduction |

---

## Coverage Summary

- **6/8 components** covered natively by MicroClaw
- **2/8 components** (Observability, Worker specialization) need extensions
- All extensions wire in via MCP (portable, standard protocol)

## Inspiration & Reference

- [Squid Club: "I Built a Discord Server Where 7 AI Agents Help Me Build My Product"](https://www.squid-club.com/blog/i-built-a-discord-server-where-7-ai-agents-help-me-build-my-product) — Author built NanoClaw. Key validated patterns: visible inter-agent communication through Discord, 4-class memory model (identical to layered-memory-model.md), constraint-based agent design over step-by-step scripts, mandatory memory for agent improvement, and "start with one agent then expand." Key warnings: agents can fabricate internal channels (enforce visible routing), bloated system prompts degrade output quality, positive feedback must be saved alongside corrections.

## Source Lists Analyzed

From https://gist.github.com/Galzi1/b2d8c6b3890ea5dab0b5654ee800b3f4:
- 🤖 Autonomous AI Agents
- 🎁 Agent Wrappers
- 💾 AI Agents Memory
- 🖥️ MCP Servers
- 📈 AI Observability
- 🧠 AI Engineering
- 🪢 Agentic Workflows and SDLC
- ✏️ Agent-First CLI Tools
- 🛡️ AI and Agent Security
- ⏲️ Productivity Tools
- 📓 AI Project Templates
