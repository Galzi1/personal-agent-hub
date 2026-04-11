---
title: Prototype MicroClaw visible-routing layer
date: 2026-04-11
priority: high
---

# Prototype MicroClaw Visible-Routing Layer

## Objective
Prove that MicroClaw can support hybrid coordination where important handoffs are announced in chat and detailed traces live in the control panel.

## Steps
1. Define a typed handoff event schema with source agent, target agent, reason, policy result, and trace link
2. Add a thin routing/policy layer over MicroClaw handoff primitives
3. Enforce allowlists, cooldowns, and loop-prevention rules for cross-agent handoffs
4. Require a chat-visible announcement for approved major handoffs
5. Persist detailed audit and run data for the same handoffs in the panel/log layer
6. Demonstrate one end-to-end routed workflow in a real or simulated chat surface

## Success Criteria
- Major handoffs appear in chat with traceable metadata
- Disallowed or throttled handoffs are blocked with explicit reasons
- The panel shows a deeper event history than the chat summary
- MicroClaw remains the execution core rather than being heavily replaced
