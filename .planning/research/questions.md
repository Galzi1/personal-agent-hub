# Research Questions

## RQ-1: Best Ollama model for agentic tool calling on available hardware
- **Date:** 2026-04-11
- **Context:** MicroClaw + Ollama architecture requires a local model that reliably handles multi-step tool calling. Model choice depends on available VRAM/RAM.
- **Key considerations:**
  - Qwen3-Coder:32B is the community consensus for best tool calling (needs ~24GB VRAM)
  - GLM-4.7-Flash and GPT-OSS:20B are alternatives for less VRAM
  - Gemma 4 is specified in the architecture diagram — verify its tool calling maturity
  - Minimum 14B parameter models for reliable agentic behavior
  - Temperature 0-0.2 recommended for tool calling
- **Action:** Benchmark 2-3 models on actual hardware before committing to one
