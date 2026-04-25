"""
One-shot script: query OpenRouter /v1/models, find best available IDs
for each task type (ranking, summarization, why_it_matters, embedding).
Prints recommended updates for config/models.yaml.
"""
import httpx
import yaml
from pathlib import Path

CONFIG_PATH = Path("config/microclaw.config.yaml")
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)
KEY = cfg["openrouter_api_key"]

HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Personal Agent Hub - find_models",
}

# Candidates to probe per task type, ordered by preference
CANDIDATES = {
    "ranking": [
        "google/gemini-2.5-flash",
        "google/gemini-2.0-flash-001",
        "google/gemini-flash-1.5",
        "anthropic/claude-haiku-4-5",
    ],
    "summarization": [
        "nvidia/llama-3.1-nemotron-ultra-253b-v1",
        "nvidia/llama-3.3-nemotron-super-49b-v1",
        "meta-llama/llama-4-maverick",
        "anthropic/claude-haiku-4-5",
    ],
    "why_it_matters": [
        "openai/gpt-4.1-mini",
        "openai/gpt-4o-mini",
        "anthropic/claude-haiku-4-5",
        "google/gemini-2.5-flash",
    ],
    "embedding": [
        "voyage/voyage-3",
        "openai/text-embedding-3-large",
        "openai/text-embedding-3-small",
        "cohere/embed-v4.0",
    ],
}

print("Fetching OpenRouter model list...")
resp = httpx.get("https://openrouter.ai/api/v1/models", headers=HEADERS, timeout=30)
resp.raise_for_status()
available_ids = {m["id"] for m in resp.json()["data"]}
print(f"  {len(available_ids)} models available\n")

print("=" * 60)
print("Recommended models.yaml updates:")
print("=" * 60)

results = {}
for task, candidates in CANDIDATES.items():
    found = next((c for c in candidates if c in available_ids), None)
    results[task] = found
    status = "OK" if found else "NONE FOUND"
    print(f"\n{task}:")
    for c in candidates:
        marker = "✓" if c in available_ids else "✗"
        print(f"  {marker} {c}")
    print(f"  => USE: {found or 'MANUAL SELECTION REQUIRED'} [{status}]")

print("\n" + "=" * 60)
print("Paste into config/models.yaml > tasks:")
print("=" * 60)
for task, model in results.items():
    if model:
        print(f"  {task}:")
        print(f'    model: "{model}"')
