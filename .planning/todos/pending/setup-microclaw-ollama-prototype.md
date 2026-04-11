---
title: Set up MicroClaw + Ollama prototype
date: 2026-04-11
priority: high
---

# Set up MicroClaw + Ollama Prototype

## Objective
Fork MicroClaw, configure Ollama as the LLM provider, and verify the foundation works for the personal-agent-hub architecture.

## Steps
1. Fork `microclaw/microclaw` to your GitHub account
2. Clone and build from source (`cargo build --release --features sqlite-vec`)
3. Install and configure Ollama with a tool-calling capable model (e.g., Qwen3-Coder:32B or Gemma 4)
4. Run `microclaw setup` and select Ollama as provider
5. Verify basic chat works via Telegram or Discord channel
6. Test sub-agent spawning (worker agent pattern)
7. Test scheduled task creation (orchestrator pattern)
8. Verify sqlite-vec embeddings work with Ollama embedding provider
9. Test MCP server integration (try `apify/apify-mcp-server`)

## Success Criteria
- MicroClaw running on Windows with Ollama as sole LLM provider
- Tool calling works reliably with chosen local model
- Sub-agents can be spawned and managed
- At least one MCP server wired in and functional
- Web UI control panel accessible at `:10961`
