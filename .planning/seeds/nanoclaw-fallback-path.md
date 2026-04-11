---
title: Evaluate NanoClaw fallback path
trigger_condition: MicroClaw development stalls or a critical blocker is hit after 3 months of use
planted_date: 2026-04-11
---

# NanoClaw Fallback Path

## Context
MicroClaw was chosen as the foundation for personal-agent-hub due to native Ollama support, built-in control panel, and vector storage. However, it's pre-1.0 (v0.1.50) with a smaller community (643⭐ vs NanoClaw's 27k⭐).

## Trigger Conditions
- MicroClaw maintainer (everettjf) goes inactive for 60+ days
- A critical bug is found that blocks the architecture and isn't fixable in-fork
- MCP integration proves unreliable in MicroClaw's Rust runtime
- Community shrinks rather than grows over 3 months

## Migration Path
1. Extract all MCP server configurations (portable — MCP is a standard protocol)
2. Set up NanoClaw with `/add-ollama-tool` skill for hybrid Claude+Ollama
3. Optionally configure `ANTHROPIC_BASE_URL` → LiteLLM → Ollama for full local
4. Rebuild control panel using `saltbo/agent-kanban` (NanoClaw has no built-in dashboard)
5. Replace sqlite-vec with `volcengine/OpenViking` for vector storage

## Key NanoClaw Advantages to Leverage
- 27k⭐ community, post-1.0 (v1.2.52)
- WhatsApp and Gmail channels (not in MicroClaw)
- Container-level security isolation
- Claude Agent SDK for highest-quality reasoning
