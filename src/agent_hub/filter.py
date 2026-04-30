import json
import logging
from datetime import datetime, timezone, timedelta
import httpx
from src.agent_hub.ingester import RawItem

logger = logging.getLogger(__name__)
RECENCY_HOURS = 48
FILTER_CAP = 150

class FilterError(Exception):
    """Raised when relevance filtering fails."""
    pass

RELEVANCE_SYSTEM_PROMPT = """You are a relevance filter for an AI news aggregator.
Your task is to analyze a batch of news items and determine if they are highly relevant to AI practitioners.

PASS criteria:
- New model releases or major model updates (e.g., GPT-5, Gemini 1.5, Claude 3).
- AI coding tools, IDE integrations, and productivity tools (Cursor, Copilot, Codex).
- New AI tools, notable product launches, or major feature announcements.
- Breakthrough research papers, novel architectures, or hot AI trends.

FAIL criteria:
- General software updates (non-AI), minor bug fixes, or maintenance releases.
- Tutorials, academy/educational content, "how-to" guides (unless they announce a new tool).
- Minor link posts, social media commentary, or opinion pieces without new data.
- RC patches or minor version bumps (e.g., Ollama v0.1.2-rc0).
- Content from openai.com/academy/ URLs (Always FAIL).

Response format:
You must respond with a JSON array of objects, each containing the 'id' (integer) and 'verdict' ('PASS' or 'FAIL').
Example: [{"id": 1, "verdict": "PASS"}, {"id": 2, "verdict": "FAIL"}]
"""

def apply_recency_window(items: list[RawItem]) -> list[RawItem]:
    """Exclude items older than RECENCY_HOURS. Items with published_at=None pass through (D-01)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENCY_HOURS)
    kept: list[RawItem] = []
    source_item_counts: dict[str, int] = {}
    source_kept_counts: dict[str, int] = {}

    for item in items:
        source_item_counts[item.source_name] = source_item_counts.get(item.source_name, 0) + 1
        if item.published_at is None:
            kept.append(item)
            source_kept_counts[item.source_name] = source_kept_counts.get(item.source_name, 0) + 1
        else:
            try:
                pub = datetime.fromisoformat(item.published_at)
            except ValueError:
                kept.append(item)
                source_kept_counts[item.source_name] = source_kept_counts.get(item.source_name, 0) + 1
                continue
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub >= cutoff:
                kept.append(item)
                source_kept_counts[item.source_name] = source_kept_counts.get(item.source_name, 0) + 1

    for source_name, total in source_item_counts.items():
        if source_kept_counts.get(source_name, 0) == 0:
            logger.warning(f"{source_name}: 0 items in 48h window - skipped")

    return kept


def relevance_filter(items: list[RawItem], model: str, api_key: str) -> list[RawItem]:
    """Filter items through OpenRouter to keep only highly relevant AI news."""
    if not items:
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "PersonalAgentHub/0.1",
    }

    user_message_parts = []
    # limit to first 50 items to prevent context/token overflow in Phase 1
    for i, item in enumerate(items[:FILTER_CAP], 1):
        user_message_parts.append(f"ID {i}: {item.title}")

    user_message = "\n".join(user_message_parts)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": RELEVANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 4096,
        "response_format": {"type": "json_object"}
    }

    last_exc = None
    for attempt in range(2):
        try:
            with httpx.Client(timeout=90.0) as client:
                resp = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                break
        except Exception as e:
            last_exc = e
            if attempt == 0:
                continue
            raise FilterError(f"HTTP call to OpenRouter failed after 2 attempts: {e}")

    try:
        raw_content = data["choices"][0]["message"]["content"]
        # Clear markdown code blocks if the model wrapped the JSON
        if "```json" in raw_content.lower():
            start = raw_content.lower().index("```json")
            fenced_content = raw_content[start:].split("```", 1)[1]
            raw_content = fenced_content.split("```", 1)[0].strip()
        elif "```" in raw_content:
            fenced_content = raw_content.split("```", 1)[1]
            raw_content = fenced_content.split("```", 1)[0].strip()
            if "\n" in raw_content:
                first_line, remainder = raw_content.split("\n", 1)
                if first_line.strip() and first_line.strip().replace("-", "").replace("_", "").isalnum():
                    raw_content = remainder.strip()

        verdicts = json.loads(raw_content)
        if not isinstance(verdicts, list):
            raise FilterError(f"OpenRouter response is not a list. Raw: {raw_content[:200]}")

        pass_ids = set()
        for v in verdicts:
            if not isinstance(v, dict) or "id" not in v or "verdict" not in v:
                continue
            if v["verdict"] == "PASS":
                pass_ids.add(v["id"])
    except (KeyError, json.JSONDecodeError, TypeError) as e:
        # Check if raw_content was defined (it should be, but being safe)
        content_for_error = locals().get("raw_content", "undefined")
        raise FilterError(f"Failed to parse OpenRouter response: {e}. Raw: {str(content_for_error)[:200]}")
    except Exception as e:
        content_for_error = locals().get("raw_content", "undefined")
        raise FilterError(f"Unexpected error parsing response: {e}. Raw: {str(content_for_error)[:200]}")

    return [item for i, item in enumerate(items, 1) if i in pass_ids]
