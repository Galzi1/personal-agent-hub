# Agent Instructions

Command environment: Windows, bash shell. Always use forward slashes in paths.

## Running the Pipeline

```bash
PYTHONPATH=src uv run --env-file .env python -m agent_hub.pipeline
```

**Setup:** Fill `.env` with:
```
OPENROUTER_API_KEY="sk-ore-..."
DISCORD_CHANNEL_ID="numeric_id_only"
MICROCLAW_DATA_DIR="C:/Users/galzi/.microclaw"
```

**Note:** Use forward slashes in Windows paths, not backslashes. Backslashes break `.env` parsing.

**Output:** Console prints `posted N messages` on success or `partial: posted X/Y messages` on mid-stream Discord failure.

## Running Tests

```bash
PYTHONPATH=. uv run pytest tests/ -q
```

All 23 tests pass.

## Module Import Path

The package is at `src/agent_hub/`. Set `PYTHONPATH` to the parent directory:
- `PYTHONPATH=src` for running as module: `python -m agent_hub.pipeline`
- `PYTHONPATH=.` for pytest in project root

## Discord Validation

After `pipeline` succeeds:
1. Check Discord channel for exactly one message batch (header + 📰 items)
2. Verify no duplicate post (MicroClaw should not re-post the `"posted N messages"` return value)
3. Check `runs` table: `SELECT status FROM runs ORDER BY run_number DESC LIMIT 1` should be `success`
