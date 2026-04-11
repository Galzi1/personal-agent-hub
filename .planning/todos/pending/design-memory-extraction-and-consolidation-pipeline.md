---
title: Design memory extraction and consolidation pipeline
date: 2026-04-11
priority: high
---

# Design Memory Extraction and Consolidation Pipeline

## Objective
Define how memories are extracted from interactions, promoted into durable stores, and periodically consolidated so the system becomes better calibrated instead of noisier over time.

## Steps
1. Define the memory classes and their write criteria
2. Separate agent-local memory from shared project memory
3. Define automatic extraction triggers for meaningful interactions
4. Add promotion rules for validated wins, corrections, and project facts
5. Design consolidation behavior for deduplication, aging, and pruning stale entries
6. Specify how traces, SQL records, vectors, and files participate in the memory pipeline

## Success Criteria
- Memory writes are automatic but bounded by clear rules
- Positive outcomes can become durable memory when validated
- Shared memory remains smaller and higher-signal than agent-local memory
- Consolidation reduces drift and duplication instead of hiding errors
