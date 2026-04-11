---
title: Layered Memory Model
date: 2026-04-11
context: Exploration of how personal-agent-hub should structure durable memory for agent calibration, project continuity, and shared context
---

# Layered Memory Model

## Decision
Use layered memory instead of one generic shared store:

- Each agent keeps its own durable memory for domain calibration and learned judgment
- A smaller shared project memory stores facts that should survive across the whole team
- Storage primitives should serve memory classes rather than define them

## Memory Classes
- **Context** - domain knowledge learned through work
- **Feedback** - corrections and validated successful patterns
- **Project** - current initiative state, decisions, and active threads
- **Reference** - pointers to external systems, sources, and stable lookup material

## Write Policy
- Memories should usually be extracted automatically after meaningful interactions
- Validated wins should be saved explicitly, not just mistakes and corrections
- Shared memory should be stricter than agent-local memory so low-signal observations do not pollute the whole system

## Hygiene Rules
- Run periodic consolidation to merge duplicates and prune stale entries
- Apply promotion rules before moving facts from interaction logs into durable memory
- Prefer bounded, curated memory over perfect recall

## Design Implications
- Do not treat SQL, vectors, and files as interchangeable memory sinks
- Design a promotion path from transient interaction logs to durable memory
- Keep agent taste and examples adjacent to memory, but distinct from instructions
