---
phase: 03-source-coverage-fix
reviewed: 2026-04-30T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - src/agent_hub/filter.py
  - src/agent_hub/discord.py
  - src/agent_hub/pipeline.py
  - tests/test_filter.py
  - tests/test_discord.py
  - tests/test_pipeline.py
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Six files were reviewed: three source modules (`filter.py`, `discord.py`, `pipeline.py`) and their corresponding test files. The implementation is largely well-structured with clear separation of concerns. However, a critical off-by-one/logic error was found in the markdown code-block stripping logic in `filter.py` that can silently discard all filter results. Additionally, there are several warnings around missing test coverage of important edge cases, a silent exception swallow in the pipeline's failure handler, a chunk-splitting bug in `discord.py` that can corrupt overflow messages, and a missing `FILTER_CAP` guard that allows items beyond the cap to be incorrectly included in results.

---

## Critical Issues

### CR-01: Markdown code-block stripping uses wrong split index - silently drops all items

**File:** `src/agent_hub/filter.py:119-121`

**Issue:** When the model returns a response wrapped in a ` ```json ` fence, the stripping logic does:
```python
raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
```
`split("```json")[-1]` correctly isolates the content after the opening fence. Then `.split("```")[0]` takes everything _before_ the first remaining backtick - which is the JSON. This path is actually correct.

However the `elif "```"` branch (line 121) has a different and **inverted** bug:
```python
raw_content = raw_content.split("```")[-1].split("```")[0].strip()
```
`split("```")[-1]` takes the **last** segment after splitting on triple-backtick. For a string like ` ```\n[...]\n``` `, splitting on ` ``` ` yields `["", "\n[...]\n", ""]`. `[-1]` is the empty string `""`. Then `.split("```")[0]` on `""` is also `""`. `json.loads("")` raises `JSONDecodeError`, which is caught and re-raised as `FilterError`, causing the entire filter run to fail and returning a failure message instead of any items.

Any model that wraps its response in a plain (non-`json`-annotated) code fence triggers this path and silently fails the run.

**Fix:**
```python
elif "```" in raw_content:
    # Take the content between the first and second fence markers
    raw_content = raw_content.split("```")[1].split("```")[0].strip()
```
Use index `[1]` (the first segment between fences), not `[-1]` (the last, which is empty).

---

## Warnings

### WR-01: `relevance_filter` applies `pass_ids` against the full `items` list but only sends `items[:FILTER_CAP]` to the LLM - IDs beyond the cap can never match, causing silent over-inclusion

**File:** `src/agent_hub/filter.py:82, 141`

**Issue:** The LLM receives `items[:FILTER_CAP]` (up to 150 items), numbered 1–N. The return filter on line 141 enumerates the full `items` list starting at 1:
```python
return [item for i, item in enumerate(items, 1) if i in pass_ids]
```
If `len(items) > FILTER_CAP`, items at positions `FILTER_CAP+1` onward are never sent to the LLM for verdict but can still appear in `pass_ids` if the LLM happened to emit those IDs (it won't, since numbering only goes to FILTER_CAP). However the real bug is the converse: if `len(items) == 150` and the LLM rates item 150 as PASS, index 150 correctly maps. But items 151+ are silently skipped _without warning_. There is no log message or counter indicating that input was truncated, so callers cannot detect this. In a high-volume run this silently drops items.

**Fix:**
```python
items_to_score = items[:FILTER_CAP]
if len(items) > FILTER_CAP:
    logger.warning(f"relevance_filter: input truncated from {len(items)} to {FILTER_CAP} items")

# ... build user_message from items_to_score ...

# Apply verdicts only against the sliced list
return [item for i, item in enumerate(items_to_score, 1) if i in pass_ids]
```

### WR-02: `format_digest` corrupts overflow chunks - strips leading newline from first item only, subsequent overflow items retain leading newlines

**File:** `src/agent_hub/discord.py:73-75`

**Issue:** When a chunk boundary is hit, the overflow logic does:
```python
chunks.append(current)
current = stripped[:CHUNK_LIMIT]
```
`stripped` is `line.lstrip("\n")` computed on line 72. This correctly removes the leading newline from the _current_ `line`. But on the next iteration, the next `line` will still start with `\n` (from `f"\n• {title}..."` on line 71), and if the new `current` fits without overflow, it gets appended as `current += line`, putting a raw `\n` at the front of a mid-chunk item. More critically, when the new `current` itself later triggers another split, `stripped = line.lstrip("\n")` applies to the new item's line, not to `current`. The first item of every overflow chunk is fine; subsequent items within an overflow chunk may start with an extra blank line, depending on Discord rendering.

Additionally, if `stripped` itself exceeds `CHUNK_LIMIT` (a single enormous line > 1800 chars), `current = stripped[:CHUNK_LIMIT]` silently truncates it mid-URL, producing a malformed Discord message.

**Fix:** Compute the chunk boundary more defensively:
```python
if len(current) + len(line) > CHUNK_LIMIT:
    chunks.append(current)
    current = line.lstrip("\n")  # strip only for the new chunk start
else:
    current += line
```
And add a guard for oversized individual lines:
```python
if len(line.lstrip("\n")) > CHUNK_LIMIT:
    logger.warning(f"Single item line exceeds chunk limit, will be truncated: {line[:80]}")
```

### WR-03: `pipeline.py` exception handler silently swallows all errors inside the `complete_run` fallback

**File:** `src/agent_hub/pipeline.py:96`

**Issue:** The outer `except Exception as e` block calls `complete_run(...)` in a nested try/except that silently ignores any secondary exception:
```python
except Exception:
    pass
```
If `complete_run` itself fails (e.g., the DB connection was never established because `sqlite3.connect` raised, meaning `conn` is unset or `run_id` is the default `"run-0-unknown"`), the original exception `e` is still returned as a formatted failure string. This is correct behavior. But because the inner `except Exception: pass` swallows everything without logging, diagnosing DB failures in production requires inspecting the returned failure string alone - the DB record is silently left in `"running"` state.

**Fix:**
```python
except Exception as db_err:
    logger.warning(f"Failed to record failure in DB: {db_err}")
```

### WR-04: `test_run_digest_partial_on_discord_failure` does not verify that the first message was actually posted - the assertion only checks `result.startswith("partial")`

**File:** `tests/test_pipeline.py:118-120`

**Issue:** The test patches `format_digest` to return `["msg1", "msg2"]` and makes the second HTTP call raise. It asserts `result.startswith("partial")` and `row[0] == "partial"`. But it never asserts that `post.call_count == 2` (called twice: once successfully, once failing). If the implementation changed to never call Discord at all and immediately return `"partial"` for any reason, the test would still pass. This makes the test unreliable as a regression guard for the partial-post behavior.

**Fix:**
```python
assert mock_client.return_value.__enter__.return_value.post.call_count == 2
```

### WR-05: `test_recency_window_mixed_items` asserts order of results that depends on insertion order - fragile if implementation changes

**File:** `tests/test_filter.py:100-102`

**Issue:** The test asserts:
```python
assert result[0].id == "recency-2"
assert result[1].id == "recency-3"
```
This relies on `apply_recency_window` returning items in input order. The current implementation does preserve insertion order, but the assertion tests internal implementation detail rather than behavior. If the function were refactored to return a set-based dedup or sorted output, the test would break without any semantic regression.

This is a mild concern but it binds the test to implementation order. More significantly, the test _omits_ verifying `result[0].id != "recency-1"` - the only real behavioral assertion should be that the old item is absent, not that the others are at specific indices.

**Fix:**
```python
ids = {item.id for item in result}
assert "recency-1" not in ids
assert "recency-2" in ids
assert "recency-3" in ids
```

---

## Info

### IN-01: Magic number `50` in comment does not match constant `FILTER_CAP = 150`

**File:** `src/agent_hub/filter.py:81`

**Issue:** The comment reads:
```python
# limit to first 50 items to prevent context/token overflow in Phase 1
```
But `FILTER_CAP = 150` on line 9. The comment is stale from an earlier value and misleads readers about the actual cap.

**Fix:** Update the comment to reflect the current constant:
```python
# Limit to first FILTER_CAP items to prevent context/token overflow
```

### IN-02: `test_format_no_items` calls `format_no_items` without the `run_id` keyword argument - tests the default, not the integration path

**File:** `tests/test_discord.py:38-39`

**Issue:**
```python
result = format_no_items(run_num=44, dt=dt)
```
The call omits `run_id`, so it tests the `run_id="unknown"` default path. The pipeline always passes an explicit `run_id`. The test asserts `"Run ID: unknown"` which only covers the default. There is no test that verifies `format_no_items` correctly embeds a real `run_id` when provided.

**Fix:** Add a complementary test with an explicit `run_id`:
```python
result = format_no_items(run_num=44, dt=dt, run_id="run-44-2026-04-26")
assert "Run ID: run-44-2026-04-26" in result
```

### IN-03: `tmp_db_conn` fixture in `conftest.py` does not call `init_db` - tests relying on DB queries will fail if schema is not initialized by the code under test

**File:** `tests/conftest.py:42-46`

**Issue:** The `tmp_db_conn` fixture yields a raw in-memory connection without calling `init_db`. This is intentional (the comment says "init_db() called by test_db.py once db.py exists"), but `test_pipeline.py` tests execute `run_digest(conn=tmp_db_conn)` which calls `init_db` internally - so the schema _is_ created. However, if a future test queries `tmp_db_conn` before running `run_digest`, the tables won't exist and the SELECT will raise. The fixture design creates a silent dependency on test execution order for correctness.

**Fix:** Either call `init_db` inside the fixture, or document clearly that the fixture is only safe after `run_digest` is called:
```python
from src.agent_hub.db import init_db

@pytest.fixture
def tmp_db_conn():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    yield conn
    conn.close()
```

---

_Reviewed: 2026-04-30T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
