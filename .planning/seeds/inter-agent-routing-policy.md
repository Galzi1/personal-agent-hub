---
title: Inter-Agent Routing Policy
trigger_condition: System expands beyond one workflow into multiple worker agents
planted_date: 2026-04-12
source: Squid Club article lessons + visible-routing-architecture.md
---

# Inter-Agent Routing Policy

## Context
The architecture diagram shows multiple Worker Agents (Resources, Ideas, News, Research, Digest) coordinating through the Orchestrator. The Squid Club article author experienced a critical failure where an agent fabricated an "internal channel" communication rather than admitting inability. His fix: 5-layer routing enforcement.

## What It Would Deliver
- Explicit permission matrix: which agents can message which others
- Self-notify blocking (agents cannot message themselves)
- Rate limiting per agent
- Per-agent-pair cooldown (e.g., 60 seconds between messages)
- Infinite loop prevention
- Rule: "If you can't see a message in Discord, it didn't happen"

## Why It Matters
visible-routing-architecture.md already states: "Treat hidden inter-agent communication as non-authoritative for major workflow transitions." But this is a design note, not an enforced policy. When the system grows beyond Phase 4, enforcement is needed.

## Current Coverage
- visible-routing-architecture.md captures the philosophy
- Phase 1 builds the Discord status channel pattern
- No enforcement mechanism exists yet (not needed for single-workflow v1)
