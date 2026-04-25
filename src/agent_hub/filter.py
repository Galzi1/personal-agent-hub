import json
import httpx
from src.agent_hub.ingester import RawItem

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
    for i, item in enumerate(items[:50], 1):
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
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[-1].split("```")[0].strip()

        verdicts = json.loads(raw_content)
        pass_ids = {v["id"] for v in verdicts if v.get("verdict") == "PASS"}
    except (KeyError, json.JSONDecodeError, TypeError) as e:
        raise FilterError(f"Failed to parse OpenRouter response: {e}. Raw: {raw_content[:200]}")

    return [item for i, item in enumerate(items, 1) if i in pass_ids]
