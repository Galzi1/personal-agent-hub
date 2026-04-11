---
title: Visible Routing Architecture
date: 2026-04-11
context: Exploration of how to adapt visible AI-agent coordination patterns into the personal-agent-hub architecture while keeping MicroClaw as the execution core
---

# Visible Routing Architecture

## Decision
Adopt a hybrid coordination model:

- Major agent handoffs, escalations, and completions should be narrated in shared chat surfaces
- The control panel should remain the detailed forensic layer for traces, audit logs, and low-level state
- MicroClaw should stay the execution core, with a thin routing/policy layer added above it

## Why
- Improves trust: important work transitions are human-visible
- Improves debugging: if a handoff matters, there is a chat artifact plus a deeper trace
- Preserves MicroClaw's strengths while compensating for weaker built-in chat-visible routing

## Design Implications
- Reframe the current Access Layer into a collaboration surface, not just ingress
- Treat hidden inter-agent communication as non-authoritative for major workflow transitions
- Add explicit handoff rules: allowed routes, cooldowns, loop prevention, and escalation thresholds
- Link chat-visible handoff events back to richer traces in the control panel

## v1 Direction
- Start with one visible workflow instead of the full worker mesh
- Prove the chat/panel visibility model before expanding the worker taxonomy
- Use the first workflow to validate routing policies, auditability, and user trust
