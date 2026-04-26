---
phase: 00-validation-spikes
plan: 03
subsystem: ingestion
tags: [watchlist, rss, feedparser, httpx, validation-spike, coverage]

requires:
  - phase: 00-validation-spikes
    provides: "Plans 00-01 and 00-02 validated runtime and model quality"
provides:
  - "7 working RSS/Atom feed URLs verified for Phase 1 use"
  - "78-item backtest dataset from past 7 days across working feeds"
  - "GO decision for R4 (watchlist coverage sufficient for v1)"
  - "Spike script at spikes/spike_watchlist.py"
  - "Results at .planning/phases/00-validation-spikes/00-03-SPIKE-RESULTS.md"
affects: [01-ingestion-foundation, any-phase-using-watchlist-feeds]

tech-stack:
  added: ["feedparser==6.0.12", "httpx==0.28.1 (already in venv)"]
  patterns: ["httpx fetch + feedparser.parse for RSS/Atom", "date field precedence: published_parsed → updated_parsed → created_parsed"]

key-files:
  created:
    - "spikes/spike_watchlist.py"
    - "spikes/watchlist_output.txt"
    - ".planning/phases/00-validation-spikes/00-03-SPIKE-RESULTS.md"
    - ".planning/phases/00-validation-spikes/00-03-SUMMARY.md"

key-decisions:
  - "GO decision for R4 - watchlist coverage sufficient for v1 (user confirmed 2026-04-25)"
  - "Cursor Changelog and Anthropic Blog have no RSS - Phase 1 should treat as unavailable or use scraping"
  - "Corrected URLs: VS Code /feed.xml (not /blogs/feed.xml), TestingCatalog /feed/ (not /rss.xml)"
  - "Simon Willison (33% of items) and TestingCatalog are highest-signal sources per volume"

patterns-established:
  - "Use httpx for fetching (handles redirects, user-agent, timeouts) then feedparser.parse(response.text)"
  - "Date field fallback chain prevents missing items from undated feeds"
  - "7/9 original feeds accessible - 2 unavailable sources are a known gap, not a blocker"

requirements-completed: ["R4"]

duration: ~20 min
completed: 2026-04-25
---

# Phase 00 / Plan 03: Watchlist Backtest Summary

**78 items collected from 7 working feeds over 7 days. Coverage assessment GO - watchlist catches major AI news stories (GPT-5.5, Images 2.0, DeepSeek V4, Workspace Agents). R4 closed. Verified URLs ready for Phase 1.**

## Performance

- **Duration:** ~20 min (script creation, URL debugging, user review)
- **Completed:** 2026-04-25
- **Tasks:** 2 (1 auto, 1 human-verify checkpoint)
- **Files created:** 4

## Accomplishments

- **Script created and runs cleanly.** `spikes/spike_watchlist.py` fetches all available feeds, filters to past 7 days, prints sorted item list with source/date/link.
- **7/9 original feeds working.** Two feeds have no RSS at all (Cursor Changelog serves HTML SPA; Anthropic Blog has no feed endpoint). Two feeds had wrong URLs that were corrected.
- **78 items collected.** Strong coverage of major AI releases this week.
- **GO decision confirmed.** User reviewed items and confirmed coverage ≥50% threshold (per D-03). R4 (watchlist coverage insufficient) closed.

## URL Findings

| Source | Status | Notes |
|--------|--------|-------|
| OpenAI Blog | OK | 18 recent / 918 total |
| DeepMind Blog | OK | 2 recent / 100 total |
| VS Code Blog | OK (corrected URL) | Was /blogs/feed.xml → /feed.xml |
| Ollama Releases | OK | 7 recent / 10 total |
| TestingCatalog | OK (corrected URL) | Was /rss.xml → /feed/ |
| Simon Willison | OK | 26 recent / 30 total (highest volume) |
| Latent Space | OK | 8 recent / 20 total |
| Cursor Changelog | UNAVAILABLE | JS-rendered SPA, no machine-readable feed |
| Anthropic Blog | UNAVAILABLE | No RSS endpoint exists |

## Deviations from Plan

- Ran script twice: first pass revealed 4 failures, second pass after URL corrections shows 7/7. Script updated with corrected URLs and comments documenting unavailable sources. This is expected spike behavior per "Handle feed URL failures" instructions in the plan.
- Coverage numbers filled in as qualitative (user confirmed GO without counting specific stories) - acceptable given D-06 "accept and move on if below threshold."

## Issues Encountered

- **Cursor Changelog:** All URL variants (feed.xml, rss.xml, rss, feed) return 200 but serve HTML. Site is a JS-rendered SPA with no RSS. Unavailable for Phase 1 RSS ingestion.
- **Anthropic Blog:** No RSS feed of any kind. All attempted paths return 404.
- **OpenAI Blog mixes news and academy/tutorial content** in same feed - Phase 1 may want to filter or deduplicate academy entries.
- **Simon Willison high volume** - includes tool releases, quotes, and minor links alongside real news. Phase 1 should consider relevance scoring.

## Notes for Phase 1

- Confirmed working feed URLs committed to SPIKE-RESULTS.md for direct reuse
- `feedparser.parse(httpx_response.text)` is the correct pattern - do not pass URLs directly to feedparser (no user-agent control)
- Latent Space AINews daily roundups are highest-value per item (curated, named releases)
- Ollama releases are frequent rc/patch noise - consider grouping in digest
- No rate limiting observed; standard User-Agent header sufficient

## Self-Check: PASSED

- [x] spikes/spike_watchlist.py exists and contains feedparser.parse
- [x] Script contains all 9 original feed entries (7 working + 2 documented as unavailable)
- [x] 00-03-SPIKE-RESULTS.md exists with Feed Status table
- [x] Results contain "Working feeds:" count
- [x] Results contain "Verified Feed URLs for Phase 1" section
- [x] Coverage Assessment filled in with GO decision
- [x] dependencies importable: feedparser, httpx

---
*Phase: 00-validation-spikes*
*Plan: 03*
*Completed: 2026-04-25*
