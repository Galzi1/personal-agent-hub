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

## RQ-2: Knowledge and memory design beyond vector-first RAG
- **Date:** 2026-04-11
- **Context:** The current direction emphasizes sqlite-vec and RAG-like capabilities, but the orchestration inspiration points toward curated long-form sources, examples, and durable memory classes as the more important differentiators.
- **Key considerations:**
  - Should agents read curated documents by table of contents and section selection instead of relying mainly on chunk retrieval?
  - Which memory classes should exist for this system (for example: context, feedback, project, reference)?
  - How should positive feedback be captured so agents remember what works, not just corrections?
  - What consolidation or dream process should merge duplicates and prune stale memories?
  - How should example corpora or taste libraries sit alongside instructions and memory?
- **Action:** Design a knowledge and memory architecture that complements MicroClaw storage without over-indexing on embeddings
