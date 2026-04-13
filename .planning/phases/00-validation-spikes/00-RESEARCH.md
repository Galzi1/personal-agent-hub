# Phase 0: Validation Spikes - Research

**Researched:** 2026-04-13
**Domain:** MicroClaw runtime validation, Ollama model quality evaluation, RSS watchlist backtesting
**Confidence:** MEDIUM

## Summary

Phase 0 consists of three sequential validation spikes that convert key project assumptions (R1, R3, R4) into evidence before committing to Phase 1 implementation. The spikes are lightweight smoke tests, not exhaustive benchmarks.

The MicroClaw spike is the most critical: it validates that the entire project's runtime foundation works on Windows. The Ollama spike validates whether a local ~32B model produces usable ranking and summarization output. The watchlist spike validates whether 9 curated RSS/Atom feeds catch enough real AI news to be useful.

**Primary recommendation:** Execute spikes sequentially (MicroClaw first, then Ollama, then watchlist). Use prebuilt Windows binaries for MicroClaw (v0.1.51 is latest), install Ollama from official installer, and write a small Python script with feedparser+httpx for the watchlist backtest.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** MicroClaw spike is a smoke test -- verify 4 critical capabilities on Windows: scheduled task execution, Discord message posting, SQLite read/write, and control panel access. Pass = all 4 work. Fail = any one blocks.
- **D-02:** Ollama spike is a quick evaluation -- run 10-15 representative tasks (ranking relevance, summarizing AI news, "why it matters" explanations). Pass/fail by user judgment: is the output usable or not?
- **D-03:** Watchlist spike is an automated feed scan -- actually fetch the 9 feeds for the past week, list all items, and user reviews which important stories are present/missing. Pass = catches at least 50% of important AI news from that week.
- **D-04:** If MicroClaw fails, fall back to NanoClaw on WSL2.
- **D-05:** If Ollama model quality fails, keep Ollama for embeddings and cheap tasks, add a remote provider (Claude or OpenAI API) for ranking and "why it matters" summaries only.
- **D-06:** If watchlist coverage falls below 50%, accept and move on. Don't block Phase 1 on watchlist size.
- **D-07:** Merge the 3 folded todos into the 3 roadmap spikes.
- **D-08:** Run spikes sequentially: MicroClaw first, then Ollama quality evaluation, then watchlist backtest.
- **D-09:** Visible-routing prototype is a stretch goal within the MicroClaw spike -- not a hard requirement.
- **D-10:** Target ~32B parameter range for the chat/ranking model (e.g., Qwen3-Coder:32B or Gemma 4:27B).
- **D-11:** Start with one model, expand if needed.
- **D-12:** Use a separate dedicated embedding model (e.g., nomic-embed-text or mxbai-embed-large) for sqlite-vec semantic retrieval.

### Claude's Discretion
- Claude picks the specific first-choice ~32B Ollama model based on current benchmarks and community feedback for ranking/summarization tasks.
- Claude picks the specific embedding model based on what works well with sqlite-vec and Ollama.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

## Standard Stack

### Core (Spike Dependencies)

| Technology | Version | Purpose | Why Standard |
|------------|---------|---------|--------------|
| **MicroClaw** | **v0.1.51** (latest) | Runtime validation target | Prebuilt Windows binary available. v0.1.51 released 2026-04-12 with memory/skill optimizations. STACK.md targets v0.1.50 but .51 is a minor patch. [VERIFIED: GitHub releases page] |
| **Ollama** | **v0.20.6** (latest) | Local LLM runtime for model evaluation | v0.20.6 released 2026-04-12 with Gemma 4 tool calling improvements. STACK.md targets v0.20.5 but .6 is a patch. [VERIFIED: GitHub releases page] |
| **Python** | **3.13.12** | Watchlist backtest script | Already installed on the machine. [VERIFIED: local environment] |
| **uv** | **0.8.13** | Python environment management | Already installed. STACK.md targets 0.11.6 but 0.8.13 is functional for spike purposes. [VERIFIED: local environment] |
| **feedparser** | **6.0.12** | RSS/Atom feed parsing | Standard Python RSS library. [CITED: STACK.md] |
| **httpx** | **0.28.1** | HTTP client for feed fetching | Async-capable, better than requests. [CITED: STACK.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MicroClaw prebuilt binary | Building from source with cargo | Prebuilt is faster for spike; build from source only needed if sqlite-vec feature required (it is NOT required for the spike's 4 core tests) |
| Qwen3 32B | Gemma 4 27B (MoE) | See model selection analysis below |

**Installation:**
```powershell
# MicroClaw -- use PowerShell installer
iwr https://microclaw.ai/install.ps1 -UseBasicParsing | iex

# Ollama -- download from official site
# https://ollama.com/download/windows

# Watchlist backtest dependencies
uv venv
uv pip install feedparser==6.0.12 httpx==0.28.1
```

## Architecture Patterns

### Spike 1: MicroClaw Validation

**What to test (4 mandatory capabilities):**

1. **Scheduled task execution:** Create a simple scheduled task via `schedule_task` tool, verify it fires within 60 seconds of its due time. The scheduler polls every 60 seconds. [VERIFIED: MicroClaw README]
2. **Discord message posting:** Configure the Discord adapter, send a test message to a designated channel. Verify message arrives with correct content.
3. **SQLite read/write:** After running the agent, inspect the SQLite database at `<data_dir>/runtime/microclaw.db` to verify session/message/memory persistence. Use `sqlite3` CLI to query.
4. **Control panel access:** With `web_enabled: true`, verify `http://127.0.0.1:10961` serves the web UI and displays runtime state.

**Stretch goal (D-09):** If all 4 pass, test visible routing -- schedule a task that triggers a sub-agent, verify the handoff is visible in both Discord chat and the control panel.

**Setup sequence:**
```powershell
# Install MicroClaw
iwr https://microclaw.ai/install.ps1 -UseBasicParsing | iex

# Run setup wizard (configures Discord token, Ollama, etc.)
microclaw setup

# Run diagnostics
microclaw doctor

# Start the runtime
microclaw start
```

**Key configuration points:**
- Discord bot token must be created at https://discord.com/developers/applications [ASSUMED]
- Ollama base URL defaults to `http://127.0.0.1:11434/v1` [VERIFIED: STACK.md version compatibility table]
- Web control panel defaults to `http://127.0.0.1:10961` [VERIFIED: MicroClaw README]

### Spike 2: Ollama Model Quality Evaluation

**Model selection recommendation (Claude's Discretion):**

**First choice: Qwen3 32B** (`ollama pull qwen3:32b`)

Rationale:
- Qwen3 32B is a dense 32B model (all parameters active per token) with strong general reasoning. Achieves 83.2% MMLU. [CITED: studyhub.net.in/techtools/best-ollama-models-in-2026]
- For ranking and summarization tasks (not coding), a general-purpose model outperforms a code-specialized one like Qwen3-Coder.
- Qwen3-Coder 30B is MoE (only 3.3B active per token) -- good for coding but may underperform on nuanced text ranking/summarization. [CITED: ollama.com/library/qwen3-coder]

**Alternative if Qwen3 32B is too slow or doesn't fit in memory: Gemma 4 27B** (`ollama pull gemma4:27b`)

Rationale:
- Gemma 4 27B is MoE with only ~3.8B active parameters per token, needs ~16GB RAM at 4-bit quantization. [CITED: gemma4.wiki/guide/gemma-4-ollama-model]
- Much faster inference but potentially lower quality for complex ranking/summarization due to fewer active parameters.
- Good fallback if the user's hardware (AMD Radeon 890M with 512MB VRAM) cannot handle a full 32B dense model.

**Hardware constraint (CRITICAL):** The user's GPU is an AMD Radeon 890M with only 512MB dedicated VRAM. This is an integrated GPU, not a discrete one. [VERIFIED: local environment probe]

**Implication:** Ollama will run in CPU-only mode or with minimal GPU offloading. A 32B dense model at Q4_K_M quantization needs ~20GB RAM. The user needs at least 32GB system RAM to run Qwen3 32B comfortably alongside the OS and MicroClaw. If the machine has only 16GB RAM, Gemma 4 27B MoE (~16GB at Q4) is the better fit. This is the single biggest hardware risk for the Ollama spike.

**Embedding model recommendation (Claude's Discretion):**

**Recommendation: nomic-embed-text** (`ollama pull nomic-embed-text`)

Rationale:
- Outperforms OpenAI text-embedding-ada-002 and text-embedding-3-small. [CITED: ollama.com/library/nomic-embed-text]
- Better on short and direct queries (57.5% vs mxbai-embed-large), which matches the typical query pattern for dedup/retrieval of news items. [CITED: arsturn.com/blog/understanding-ollamas-embedding-models]
- Smaller and faster than mxbai-embed-large, important given the CPU-bound environment.
- 768 dimensions, well-suited for sqlite-vec. [ASSUMED]

**Evaluation protocol:**
```
Prepare 10-15 test tasks:
- 5 ranking tasks: "Given these 5 AI news items, rank by relevance to [topic]"
- 5 summarization tasks: "Summarize this AI news item in 2-3 sentences"
- 3-5 "why it matters" tasks: "Explain why this matters for someone who builds with AI tools"

For each task:
1. Run against the model via Ollama API or CLI
2. Record output
3. User judges: usable (pass) or not usable (fail)
4. Note latency per task

Pass criteria: majority of tasks produce usable output
```

### Spike 3: Watchlist Backtest

**The 9 starter feeds** (from RISK-REVIEW.md A3):
1. OpenAI blog
2. Google DeepMind blog
3. Cursor changelog/blog
4. Claude Code / Anthropic blog
5. VS Code Copilot updates
6. Ollama releases (GitHub releases.atom)
7. TestingCatalog
8. Simon Willison's blog
9. Latent Space podcast/blog

**Backtest approach:**

RSS feeds only contain current items (typically last 10-50 entries per feed). They do NOT have a "fetch historical" API. The backtest must:

1. Fetch all 9 feeds NOW using feedparser
2. Filter entries by published date to the past 7 days
3. Collect all items with: title, link, published date, source name
4. Present the full list to the user for manual review
5. User compares against their memory of "what was important this week in AI"
6. Count: important stories caught vs. important stories missed
7. Pass if >= 50% coverage (D-03)

**Important caveat:** If a feed has already rotated out items older than 7 days, those items will be missed by this backtest. This is a known limitation -- RSS feeds are point-in-time snapshots. The backtest measures "what the feeds currently expose," not a complete historical archive. [ASSUMED]

**Script structure:**
```python
# spike_watchlist.py
import feedparser
import httpx
from datetime import datetime, timedelta

FEEDS = {
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "DeepMind Blog": "https://deepmind.google/blog/rss.xml",
    "Cursor Changelog": "https://changelog.cursor.com/feed.xml",
    "Anthropic Blog": "https://www.anthropic.com/rss.xml",
    "VS Code Copilot": "https://code.visualstudio.com/blogs/feed.xml",
    "Ollama Releases": "https://github.com/ollama/ollama/releases.atom",
    "TestingCatalog": "https://testingcatalog.com/rss.xml",
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Latent Space": "https://www.latent.space/feed",
}
# NOTE: Feed URLs above are best-guess and MUST be verified during execution.
# Some may be wrong or have changed. Part of the spike is discovering correct URLs.

cutoff = datetime.now() - timedelta(days=7)
# Parse each feed, filter by date, collect items, print report
```

### Anti-Patterns to Avoid
- **Over-engineering the spikes:** These are smoke tests, not production code. Scripts should be disposable.
- **Building infrastructure during validation:** Don't set up project structure, CI, or tests during Phase 0. That's Phase 1's job.
- **Testing too many models:** D-11 says start with one model. Only test a second if the first clearly fails.
- **Blocking on watchlist coverage:** D-06 says accept < 50% and move on. Don't expand the watchlist during Phase 0.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS parsing | Custom XML parser | feedparser 6.0.12 | Handles RSS 0.9x, 1.0, 2.0, Atom 1.0, CDF, JSON feeds, and all their quirks |
| Discord bot | discord.py bot framework | MicroClaw's native Discord adapter | The spike validates MicroClaw's Discord support, not a custom bot |
| Task scheduling | Windows Task Scheduler or cron | MicroClaw's built-in scheduler | The spike validates MicroClaw's scheduler specifically |
| LLM API wrapper | Custom Ollama HTTP client | `ollama run` CLI or MicroClaw's provider layer | CLI is sufficient for evaluation; no need for custom API code |

## Common Pitfalls

### Pitfall 1: MicroClaw Prebuilt Binary vs. Source Build Confusion
**What goes wrong:** User tries to build from source with `--features sqlite-vec` when the prebuilt binary is sufficient for the spike, wasting time on Rust compilation issues on Windows.
**Why it happens:** STACK.md recommends `cargo build --release --features sqlite-vec`, which is the production path but NOT needed for Phase 0 smoke testing.
**How to avoid:** Use the prebuilt binary (`iwr https://microclaw.ai/install.ps1 -UseBasicParsing | iex`) for the spike. The 4 core tests (scheduler, Discord, SQLite, control panel) don't require the sqlite-vec feature. Sqlite-vec build can wait for Phase 1.
**Warning signs:** Encountering Rust toolchain errors, linker errors, or missing C dependencies during compilation.

### Pitfall 2: Ollama Model Too Large for Available RAM
**What goes wrong:** User pulls a 32B dense model that requires ~20GB RAM, machine runs out of memory, Ollama swaps to disk, inference takes minutes per response.
**Why it happens:** The machine has an AMD Radeon 890M (512MB VRAM, integrated GPU). All inference will be CPU-bound with system RAM.
**How to avoid:** Check total system RAM before pulling models. If < 32GB, start with Gemma 4 27B MoE (needs ~16GB). If >= 32GB, try Qwen3 32B.
**Warning signs:** `ollama run` hangs, system becomes unresponsive, Windows starts paging heavily.

### Pitfall 3: RSS Feed URLs Are Wrong or Changed
**What goes wrong:** The feed URLs assumed in the watchlist don't work -- 404 errors, redirects, or the feed format has changed.
**Why it happens:** Feed URLs are not stable over time. The starter list was researched weeks ago and URLs were never tested.
**How to avoid:** The FIRST step of the watchlist spike should be verifying each feed URL returns valid RSS/Atom XML. Log which feeds work and which don't. A failed feed is a data point, not a blocker.
**Warning signs:** feedparser returns empty entries, HTTP 404/403, or HTML instead of XML.

### Pitfall 4: Discord Bot Token Not Set Up
**What goes wrong:** The MicroClaw Discord adapter fails to connect because no Discord bot application has been created or the token hasn't been configured.
**Why it happens:** MicroClaw setup wizard asks for a Discord token, but the user hasn't created a Discord application/bot yet.
**How to avoid:** Create the Discord bot application BEFORE running `microclaw setup`. Steps: Discord Developer Portal > New Application > Bot > Copy Token > Also enable Message Content Intent.
**Warning signs:** MicroClaw starts but shows "Discord adapter: disconnected" or authentication errors.

### Pitfall 5: Confusing "Spike Pass" with "Production Ready"
**What goes wrong:** MicroClaw smoke test passes but the team assumes all Phase 1 features will work smoothly.
**Why it happens:** A smoke test of 4 capabilities doesn't cover edge cases, error handling, concurrent operations, or long-running reliability.
**How to avoid:** Record what was tested AND what was NOT tested. The spike answers "can it do the basics?" not "will it handle everything Phase 1 needs?"
**Warning signs:** Overconfidence after a clean spike; skipping risk monitoring in Phase 1.

## Code Examples

### MicroClaw Scheduled Task Test
```
# Via MicroClaw chat interface (Discord or Web):
"Schedule a task to say 'Hello from scheduled task' every 5 minutes"

# Verify via:
"List my scheduled tasks"
"Show task history"
```
[ASSUMED -- based on MicroClaw README description of natural-language task management]

### Ollama Model Evaluation
```bash
# Pull the model
ollama pull qwen3:32b

# Test ranking (via CLI)
ollama run qwen3:32b "Given these 3 AI news items, rank them by importance for someone who builds AI-powered tools:
1. OpenAI released GPT-5 with improved reasoning
2. A new VS Code extension adds AI code review
3. Python 3.14 adds experimental JIT compiler
Reply with just the ranking and a one-sentence reason for each."

# Test summarization
ollama run qwen3:32b "Summarize this in 2-3 sentences for a developer audience: [paste a real AI news article]"

# Test 'why it matters'
ollama run qwen3:32b "Explain in 2 sentences why this matters for someone who builds with AI tools: [paste headline + first paragraph]"
```
[VERIFIED: Ollama CLI usage pattern from ollama.com docs]

### Watchlist Feed Verification
```python
import feedparser

url = "https://simonwillison.net/atom/everything/"
feed = feedparser.parse(url)
print(f"Feed title: {feed.feed.get('title', 'N/A')}")
print(f"Entries: {len(feed.entries)}")
for entry in feed.entries[:3]:
    print(f"  - {entry.get('title', 'N/A')} ({entry.get('published', 'no date')})")
```
[VERIFIED: feedparser standard usage pattern]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MicroClaw v0.1.50 | v0.1.51 available | 2026-04-12 | Minor -- memory/skill optimizations. Use .51. |
| Ollama v0.20.5 | v0.20.6 available | 2026-04-12 | Minor -- Gemma 4 tool calling fix. Use .6. |
| uv 0.8.13 (installed) | uv 0.11.6 (STACK.md target) | Unknown | uv 0.8.13 is functional for spike. Upgrade not needed in Phase 0. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Feed URLs for the 9 starter sources are approximately correct | Spike 3 architecture | Low -- verifying URLs is part of the spike; wrong URLs are data, not blockers |
| A2 | nomic-embed-text produces 768-dimension vectors compatible with sqlite-vec | Embedding model recommendation | Low -- embedding model is not tested in Phase 0, only in Phase 1+ |
| A3 | Discord bot creation requires Message Content Intent enabled | Pitfall 4 | Medium -- if MicroClaw needs specific intents not documented, setup will fail |
| A4 | MicroClaw prebuilt binary includes SQLite support without needing sqlite-vec build flag | Pitfall 1 | Medium -- if prebuilt lacks SQLite entirely, would need source build |
| A5 | User has >= 16GB system RAM for running Ollama models | Ollama hardware constraint | High -- if < 16GB, even Gemma 4 27B MoE won't run well |
| A6 | MicroClaw `setup` wizard handles Discord adapter configuration interactively | Setup sequence | Medium -- if it requires manual config file editing, setup instructions need adjusting |

## Open Questions

1. **How much system RAM does the target machine have?**
   - What we know: GPU is AMD Radeon 890M (integrated, 512MB VRAM). CPU inference only.
   - What's unclear: Total system RAM. This determines whether Qwen3 32B (needs ~20GB) or Gemma 4 27B MoE (needs ~16GB) is feasible.
   - Recommendation: Check RAM first (`systeminfo | findstr "Total Physical Memory"`). If < 32GB, default to Gemma 4 27B.

2. **Does the MicroClaw prebuilt Windows binary include SQLite support out of the box?**
   - What we know: The prebuilt binary is 16.2MB. SQLite is described as the default storage backend.
   - What's unclear: Whether "default" means it's always bundled, or if it requires the sqlite-vec feature flag.
   - Recommendation: Install prebuilt and run `microclaw doctor` to check. Regular SQLite (without vec) should be bundled.

3. **Does the user already have a Discord server and bot token ready?**
   - What we know: The project targets Discord delivery.
   - What's unclear: Whether the Discord application/bot has been created.
   - Recommendation: Create the Discord application before starting the MicroClaw spike.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| MicroClaw | Spike 1 | Not installed | -- | Install via PowerShell one-liner |
| Ollama | Spike 2 | Not installed | -- | Install via OllamaSetup.exe from ollama.com |
| Python | Spike 3 | Available | 3.13.12 | -- |
| uv | Spike 3 | Available | 0.8.13 | pip works too |
| Cargo/Rust | NOT NEEDED for spike | Available | 1.94.1 | Only needed if source build required |
| NVIDIA GPU | Ollama acceleration | Not available | -- | CPU-only inference (slower but functional) |
| Discord bot token | Spike 1 | Unknown | -- | Must be created at Discord Developer Portal |
| sqlite3 CLI | Spike 1 verification | Unknown | -- | Can verify SQLite via MicroClaw control panel instead |

**Missing dependencies with no fallback:**
- None -- all missing tools (MicroClaw, Ollama) have straightforward installers.

**Missing dependencies with fallback:**
- GPU acceleration: Not available (AMD integrated GPU). Fallback: CPU inference. Impact: slower Ollama responses (seconds to minutes per query vs. sub-second with GPU).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual validation (spikes are smoke tests, not automated test suites) |
| Config file | None -- Phase 0 does not establish test infrastructure |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements to Test Map
Phase 0 has no formal requirement IDs (risk mitigation, not feature delivery). Validation is structured as go/no-go decisions:

| Spike | Behavior | Test Type | Validation Method | Automated? |
|-------|----------|-----------|-------------------|------------|
| MicroClaw | Scheduler fires on time | Manual smoke test | Schedule task, observe execution | No |
| MicroClaw | Discord posting works | Manual smoke test | Send message, verify in Discord | No |
| MicroClaw | SQLite persists data | Manual smoke test | Query microclaw.db after run | No |
| MicroClaw | Control panel accessible | Manual smoke test | Open http://127.0.0.1:10961 | No |
| Ollama | Model produces usable output | Manual quality judgment | Run 10-15 tasks, user evaluates | No |
| Watchlist | Feeds return recent items | Semi-automated | Python script fetches and lists | Partially |
| Watchlist | Coverage >= 50% | Manual review | User compares items vs. known news | No |

### Wave 0 Gaps
- None -- Phase 0 intentionally does not create test infrastructure. Test framework setup belongs in Phase 1.

## Security Domain

Phase 0 is a validation-only phase with no production code. Security considerations are minimal:

| ASVS Category | Applies | Notes |
|---------------|---------|-------|
| V2 Authentication | No | No auth in spikes |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | Single user, local only |
| V5 Input Validation | No | No user input processing |
| V6 Cryptography | No | No crypto operations |

**Sole security note:** The Discord bot token is a secret. During the MicroClaw spike, ensure the token is stored in MicroClaw's config (not committed to git) and that the `.gitignore` excludes MicroClaw's data directory.

## Sources

### Primary (HIGH confidence)
- [MicroClaw GitHub README](https://github.com/microclaw/microclaw) -- verified Discord adapter, scheduler (60s poll), SQLite default, web control panel (port 10961), PowerShell installer, `microclaw setup`/`doctor`/`start` commands
- [MicroClaw Releases](https://github.com/microclaw/microclaw/releases) -- verified v0.1.51 (2026-04-12), Windows binary available (16.2MB)
- [Ollama GitHub Releases](https://github.com/ollama/ollama/releases) -- verified v0.20.6 (2026-04-12) as latest
- [Ollama Download](https://ollama.com/download/windows) -- verified Windows installer availability
- Local environment probes -- verified Python 3.13.12, uv 0.8.13, Cargo 1.94.1, AMD Radeon 890M (512MB VRAM)

### Secondary (MEDIUM confidence)
- [Qwen3 32B on Ollama](https://ollama.com/library/qwen3:32b) -- model availability confirmed
- [Gemma 4 27B on Ollama](https://ollama.com/library/gemma4:27b) -- model availability confirmed, MoE architecture with ~3.8B active params
- [nomic-embed-text on Ollama](https://ollama.com/library/nomic-embed-text) -- embedding model availability confirmed
- [Best Ollama Models 2026](https://studyhub.net.in/techtools/best-ollama-models-in-2026-top-10-ranked-by-use-case-hardware/) -- Qwen3 32B MMLU score 83.2%
- [Embedding model comparison](https://www.arsturn.com/blog/understanding-ollamas-embedding-models) -- nomic-embed-text vs mxbai-embed-large accuracy comparison
- `.planning/research/STACK.md` -- project stack decisions
- `.planning/RISK-REVIEW.md` -- R1, R3, R4 risk definitions and starter watchlist composition

### Tertiary (LOW confidence)
- Feed URLs for the 9 starter sources -- best-guess URLs that must be verified during execution

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- MicroClaw/Ollama versions verified against GitHub releases, Python/uv verified locally
- Architecture (spike design): MEDIUM -- MicroClaw configuration details assumed from README, not personally tested
- Pitfalls: MEDIUM -- based on domain knowledge and hardware analysis, not prior experience with MicroClaw on this specific hardware
- Model selection: MEDIUM -- based on benchmark data and community reports, not personal evaluation

**Research date:** 2026-04-13
**Valid until:** 2026-04-20 (7 days -- fast-moving tools, versions may change)
