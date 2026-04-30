# Requirements: Personal Agent Hub

**Defined:** 2026-04-11  
**Core Value:** Deliver a high-signal, low-noise AI intelligence feed early enough to be useful, instead of making the user hunt through repetitive posts after everyone else has already amplified them.

## v1 Requirements

### Sources

- [x] **SRC-01**: User receives candidate updates gathered from a curated multi-source watchlist rather than a single feed. *(Phase 1 - complete 2026-04-26)*
- [ ] **SRC-02**: User can define tracked topics covering model releases, AI coding tools, useful new AI tools, and hot trends.

### Signal

- [ ] **SIG-01**: User receives one digest item per underlying story even when many sources cover the same update.
- [ ] **SIG-02**: User receives a ranked shortlist of the most relevant daily stories instead of a raw chronological feed.
- [ ] **SIG-03**: Each digest item includes a short "why it matters" explanation.
- [ ] **SIG-04**: User can distinguish confirmed updates from uncertain or disputed items in the digest.

### Digest

- [x] **DGST-01**: User receives the daily digest in Discord. *(Phase 2 - complete 2026-04-27)*
- [ ] **DGST-02**: Each digest item includes citations to the supporting source links.
- [ ] **DGST-03**: User can scan digest sections for model releases, AI coding tools, new AI tools, and hot trends.
- [x] **DGST-04**: User can see whether the daily digest run completed, failed, or produced no qualifying items. *(Phase 1 - complete 2026-04-26)*

### Feedback

- [ ] **FDBK-01**: User can mute a source from future digests.
- [ ] **FDBK-02**: User can mute a topic from future digests.
- [ ] **FDBK-03**: User can mark a digest item as more useful or less useful with simple feedback controls.

## v2 Requirements

### Personalization

- **PERS-01**: System prioritizes stories by first-seen novelty relative to prior digest coverage.
- **PERS-02**: System learns durable topic, source, and signal preferences from repeated user feedback.
- **PERS-03**: System identifies multi-day trend rollups across recurring signals.

### Actions

- **ACT-01**: User can save a digest item as a resource for later reference.
- **ACT-02**: User can convert a digest item into a post idea.
- **ACT-03**: User can watch a company, tool, or model for future briefs.

### Expansion

- **RSCH-01**: User can receive competitor, prospect, or partner monitoring briefs.
- **CHAN-01**: User can receive the digest in additional channels beyond Discord.
- **ALRT-01**: User can receive selective urgent alerts for exceptional events outside the daily digest.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time alert firehose | Recreates the noise problem the product is meant to solve; selective alerts belong later. |
| Automatic social posting | Adds tone, trust, and brand risk before the core intel workflow is proven. |
| Multi-user collaboration | v1 is explicitly single-user. |
| Telegram, Slack, or WhatsApp delivery at launch | Discord is the first delivery surface and should be proven before adding channels. |
| Save-as-resource and save-as-post actions in v1 | Explicitly deferred until digest quality is validated. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SRC-01 | Phase 1 | Complete 2026-04-26 |
| SRC-02 | Phase 3 | Pending |
| SIG-01 | Phase 6 | Pending |
| SIG-02 | Phase 10 | Pending |
| SIG-03 | Phase 10 | Pending |
| SIG-04 | - | Unmapped (no current phase) |
| DGST-01 | Phase 2 | Complete 2026-04-27 |
| DGST-02 | Phase 10 | Pending |
| DGST-03 | Phase 10 | Pending |
| DGST-04 | Phase 1 | Complete 2026-04-26 |
| FDBK-01 | - | Deferred (phase removed from roadmap) |
| FDBK-02 | - | Deferred (phase removed from roadmap) |
| FDBK-03 | - | Deferred (phase removed from roadmap) |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 9
- Unmapped/deferred: 4 (SIG-04, FDBK-01, FDBK-02, FDBK-03)

---
*Requirements defined: 2026-04-11*  
*Last updated: 2026-04-27 - traceability corrected to match current roadmap (phases 1-10)*
