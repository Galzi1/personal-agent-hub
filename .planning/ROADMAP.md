# Roadmap: Personal Agent Hub

## Overview

This roadmap delivers one explicit daily AI-intelligence workflow from end to end: start with trustworthy multi-source intake and observable run status, turn overlapping coverage into canonical stories, compose a ranked Discord digest with citations and clear relevance cues, then add feedback controls that suppress noise and improve future runs without expanding beyond the core digest loop.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Ingestion Foundation & Run Visibility** - Establish curated intake and make each daily digest run observable.
- [ ] **Phase 2: Canonical Story Formation** - Collapse overlapping coverage into trustworthy story records with visible confidence.
- [ ] **Phase 3: Ranked Discord Digest** - Deliver a short, topic-aware, cited AI digest in Discord.
- [ ] **Phase 4: Feedback & Suppression** - Let the user shape future digests with direct feedback and mutes.

## Phase Details

### Phase 1: Ingestion Foundation & Run Visibility
**Goal**: User can rely on a local-first daily digest workflow that gathers candidate updates from a curated watchlist and makes each run outcome visible.
**Depends on**: Nothing (first phase)
**Requirements**: SRC-01, DGST-04
**Success Criteria** (what must be TRUE):
  1. User receives candidate updates gathered from a curated multi-source watchlist rather than a single feed.
  2. User can see whether the daily digest run completed, failed, or produced no qualifying items.
  3. User can tell which daily run produced the visible outcome instead of seeing an untraceable status message.
**Plans**: TBD

### Phase 2: Canonical Story Formation
**Goal**: User gets one trustworthy story per underlying update, with uncertainty visible before stories are selected into the digest.
**Depends on**: Phase 1
**Requirements**: SIG-01, SIG-04
**Success Criteria** (what must be TRUE):
  1. User receives one story candidate per underlying update even when many sources cover the same event.
  2. User does not see the same underlying update repeated as separate stories after duplicate coverage is collapsed.
  3. User can distinguish confirmed updates from uncertain or disputed items.
**Plans**: TBD

### Phase 3: Ranked Discord Digest
**Goal**: User receives a short, relevant, topic-aware daily digest in Discord that explains why each selected story matters.
**Depends on**: Phase 2
**Requirements**: SRC-02, SIG-02, SIG-03, DGST-01, DGST-02, DGST-03
**Success Criteria** (what must be TRUE):
  1. User receives the daily digest in Discord.
  2. User can scan separate digest sections for model releases, AI coding tools, new AI tools, and hot trends.
  3. User receives a ranked shortlist of the most relevant daily stories instead of a raw chronological feed.
  4. Each digest item includes supporting source citations and a short "why it matters" explanation.
  5. User can define tracked topics that influence what appears in the digest.
**Plans**: TBD

### Phase 4: Feedback & Suppression
**Goal**: User can calibrate future digests directly by suppressing noise and marking which items were useful.
**Depends on**: Phase 3
**Requirements**: FDBK-01, FDBK-02, FDBK-03
**Success Criteria** (what must be TRUE):
  1. User can mute a source so it no longer appears in future digests.
  2. User can mute a topic so it no longer appears in future digests.
  3. User can mark a digest item as more useful or less useful with simple feedback controls.
  4. User can observe later digests reflecting those mute and usefulness signals.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Ingestion Foundation & Run Visibility | 0/TBD | Not started | - |
| 2. Canonical Story Formation | 0/TBD | Not started | - |
| 3. Ranked Discord Digest | 0/TBD | Not started | - |
| 4. Feedback & Suppression | 0/TBD | Not started | - |
