---
title: Set up MicroClaw + Ollama prototype
date: 2026-04-11
priority: high
status: done
resolved: 2026-04-24
resolution: Folded into Phase 0 Plan 00-01 (MicroClaw smoke test) and Plan 00-02 (LLM provider eval). MicroClaw validated GO on 2026-04-23 (all 4 smoke tests PASS). LLM provider pivoted from local Ollama to OpenRouter per D-13 (RAM constraint: 6.4 GB free, 32B local infeasible). Plan 00-02 evaluates OpenRouter per-task model matrix instead of local Ollama.
---

# Set up MicroClaw + Ollama Prototype

## Objective
Fork MicroClaw, configure Ollama as the LLM provider, and verify the foundation works for the personal-agent-hub architecture.

## Resolution (2026-04-24)

Completed via Phase 0 Plan 00-01 (MicroClaw smoke test - GO) and Plan 00-02 (OpenRouter model quality eval - pending).

**MicroClaw status:** Validated on Windows 11 x86_64. Scheduler, Discord outbound, SQLite persistence, and control panel all PASS. See `.planning/phases/00-validation-spikes/00-01-SPIKE-RESULTS.md`.

**LLM provider:** Pivoted from local Ollama to OpenRouter. Original Ollama setup steps are moot. Plan 00-02 establishes `config/models.yaml` with per-task OpenRouter model selection instead.

**Divergences from original steps:**
- Step 1-2 (fork/build from source): Used pre-built binary at `C:\microclaw\microclaw` instead.
- Step 3 (Ollama + local model): Replaced by OpenRouter API key + `config/models.yaml`. Local inference not viable given hardware constraints.
- Step 4 (microclaw setup with Ollama): MicroClaw configured with OpenRouter via `config/microclaw.config.yaml`.
- Steps 5-9: Partially covered by Plan 00-01 (Discord, scheduled tasks, control panel). Sub-agent spawning + MCP integration deferred to Phase 1.

## Original Steps (archived for reference)
1. Fork `microclaw/microclaw` to your GitHub account
2. Clone and build from source (`cargo build --release --features sqlite-vec`)
3. Install and configure Ollama with a tool-calling capable model (e.g., Qwen3-Coder:32B or Gemma 4)
4. Run `microclaw setup` and select Ollama as provider
5. Verify basic chat works via Telegram or Discord channel
6. Test sub-agent spawning (worker agent pattern)
7. Test scheduled task creation (orchestrator pattern)
8. Verify sqlite-vec embeddings work with Ollama embedding provider
9. Test MCP server integration (try `apify/apify-mcp-server`)
