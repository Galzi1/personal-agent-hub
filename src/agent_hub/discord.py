from datetime import datetime

CHECKMARK = "\u2705"
CROSSMARK = "\u274c"
WARNING   = "\u26a0\ufe0f"
ARROW     = "\u2192"

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
