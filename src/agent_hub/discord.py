from datetime import datetime
import httpx

CHECKMARK = "\u2705"
CROSSMARK = "\u274c"
WARNING   = "\u26a0\ufe0f"
ARROW     = "\u2192"
NEWSPAPER = "\U0001f4f0"
CHUNK_LIMIT = 1800

def format_success(run_num: int, raw: int, relevant: int, sources: int, dt: datetime, run_id: str = "unknown") -> str:
    """Format success message for Discord."""
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return f"{CHECKMARK} Run #{run_num} - {ts}\n{raw} fetched {ARROW} {relevant} relevant items from {sources} sources\nRun ID: {run_id}"

def format_failure(run_num: int, error: str, run_id: str, dt: datetime) -> str:
    """Format failure message for Discord."""
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return f"{CROSSMARK} Run #{run_num} failed - {ts}\n{error}\nRun ID: {run_id}"

def format_no_items(run_num: int, dt: datetime, run_id: str = "unknown") -> str:
    """Format message when no items are relevant."""
    ts = dt.strftime("%Y-%m-%d %H:%M")
    return f"{WARNING} Run #{run_num} - {ts}\n0 relevant items (all sources returned no new AI content)\nRun ID: {run_id}"


def format_digest(
    items: list,
    run_num: int,
    dt: datetime,
    run_id: str,
    raw_count: int,
    source_count: int,
) -> list[str]:
    """Format items into one or more Discord-ready message strings (max ~1800 chars each).

    First string: status header + intro line + initial items.
    Subsequent strings: overflow items only.
    Returns list[str] per D-10.
    """
    header = format_success(run_num, raw_count, len(items), source_count, dt, run_id)
    intro = f"\n{NEWSPAPER} Today\u2019s AI updates:"
    chunks: list[str] = []
    current = header + intro

    for item in items:
        title = item.title[:80] if len(item.title) > 80 else item.title
        line = f"\n\u2022 {title} [{item.source_name}]\n  <{item.link}>"
        stripped = line.lstrip("\n")
        if len(current) + len(line) > CHUNK_LIMIT:
            chunks.append(current)
            current = stripped[:CHUNK_LIMIT]
        else:
            current += line

    chunks.append(current)
    return chunks


def post_to_discord(messages: list[str], token: str, channel_id: str) -> int:
    """Post messages to Discord REST API. Returns count of successfully posted messages.

    Returns partial count on HTTP error so caller can detect mid-stream failure.
    """
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    posted = 0
    with httpx.Client(timeout=30.0) as client:
        for msg in messages:
            try:
                resp = client.post(url, headers=headers, json={"content": msg})
                resp.raise_for_status()
            except (httpx.HTTPStatusError, httpx.RequestError):
                if posted == 0:
                    raise
                return posted
            posted += 1
    return posted
