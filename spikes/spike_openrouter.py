"""
OpenRouter Model Quality Evaluation Spike - Phase 0, Plan 00-02
Verifies D-18 starter model IDs and runs 10-15 representative AI feed tasks.
Outputs results to stdout for capture into MODEL-EVALUATION-RESULTS.md.
"""

import httpx
import yaml
import time
import sys
from pathlib import Path

# Load config - no hardcoded API key or model IDs (D-17, D-20)
CONFIG_PATH = Path("config/microclaw.config.yaml")
MODELS_PATH = Path("config/models.yaml")

try:
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    OPENROUTER_KEY = cfg["openrouter_api_key"]
    if not OPENROUTER_KEY:
        raise ValueError(f"openrouter_api_key is empty in {CONFIG_PATH}")
except FileNotFoundError:
    print(f"Error: Configuration file not found at {CONFIG_PATH}")
    sys.exit(1)
except ValueError as e:
    print(f"Error loading configuration: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading config: {e}")
    sys.exit(1)


try:
    with open(MODELS_PATH) as f:
        models_cfg = yaml.safe_load(f)
    MODELS = {k: v["model"] for k, v in models_cfg["tasks"].items()}
except FileNotFoundError:
    print(f"Error: Models file not found at {MODELS_PATH}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading models: {e}")
    sys.exit(1)

BASE_URL = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Personal Agent Hub Spike",
}

# D-22: $20 hard cap; abort at $18 to give buffer
SPEND_CAP = 18.0
total_cost_usd = 0.0

# Fallback model IDs per D-16 and D-18
FALLBACKS = {
    "ranking": "google/gemini-2.5-flash",
    "summarization": "nvidia/nemotron-3-super-120b-a12b",
    "why_it_matters": "openai/gpt-5.4",
    "embedding": "voyage-3",
}
EMBEDDING_FALLBACK_2 = "openai/text-embedding-3-large"


def check_spend():
    global total_cost_usd
    if total_cost_usd >= SPEND_CAP:
        print(
            f"\n[ABORT] Cumulative spend ${total_cost_usd:.4f} reached ${SPEND_CAP} cap (D-22). Halting."
        )
        sys.exit(1)


def chat(task_type: str, prompt: str, model_override: str | None = None) -> dict:
    global total_cost_usd
    check_spend()
    model = model_override or MODELS[task_type]
    start = time.monotonic()
    try:
        resp = httpx.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADERS,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
            },
            timeout=90,
        )
        resp.raise_for_status()
        elapsed = time.monotonic() - start
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError(f"Empty choices in response: {data.get('error', data)}")
        content = choices[0]["message"]["content"]
        usage = data.get("usage", {})
        cost = usage.get("cost", 0.0) or 0.0
        total_cost_usd += cost
        return {
            "status": "ok",
            "model": model,
            "content": content,
            "latency_s": round(elapsed, 2),
            "tokens": usage,
            "cost_usd": cost,
        }
    except Exception as e:
        return {
            "status": "error",
            "model": model,
            "error": str(e),
            "latency_s": round(time.monotonic() - start, 2),
        }


def embed(text: str, model_override: str | None = None) -> dict:
    # Check spend before embedding, as it can be costly
    check_spend()
    model = model_override or MODELS["embedding"]
    start = time.monotonic()
    try:
        resp = httpx.post(
            f"{BASE_URL}/embeddings",
            headers=HEADERS,
            json={"model": model, "input": text},
            timeout=30,
        )
        elapsed = time.monotonic() - start
        if resp.status_code != 200:
            return {
                "status": "fail",
                "model": model,
                "http_status": resp.status_code,
                "body": resp.text[:200],
                "latency_s": round(elapsed, 2),
            }
        data = resp.json()["data"][0]["embedding"]
        # Cost tracking for embeddings is less reliable directly from response, use a placeholder or manual check if needed
        # For now, assume embeddings are less costly or covered by general check_spend
        return {
            "status": "ok",
            "model": model,
            "dimensions": len(data),
            "sample": data[:4],
            "latency_s": round(elapsed, 2),
        }
    except Exception as e:
        return {"status": "error", "model": model, "error": str(e)}


def verify_models(required_ids: list[str]) -> dict[str, bool]:
    try:
        resp = httpx.get(f"{BASE_URL}/models", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        available = {m["id"] for m in resp.json()["data"]}
        return {mid: mid in available for mid in required_ids}
    except Exception as e:
        print(f"Error verifying models against /v1/models: {e}")
        # Return all as False if the /models endpoint fails
        return {mid: False for mid in required_ids}


def sep(title=""):
    print(f"\n{'=' * 70}")
    if title:
        print(title)
        print("=" * 70)


# ─── STEP A: Model availability verification ──────────────────────────────
sep("STEP A: VERIFY MODEL AVAILABILITY (/v1/models)")

required = list(MODELS.values())
print(f"Checking {len(required)} D-18 starters...")
avail = verify_models(required)

effective_models = dict(MODELS)
findings = []

for task, model_id in MODELS.items():
    found = avail.get(model_id, False)
    if found:
        print(f"  FOUND: {task} -> {model_id}")
    else:
        fallback = FALLBACKS.get(task)
        if fallback:
            effective_models[task] = fallback
            msg = f"  MISSING: {task} -> {model_id}  [alt-picked fallback: {fallback}]"
            print(msg)
            findings.append(
                {
                    "finding": f"F-MODEL-{task.upper()}",
                    "detail": f"D-18 starter '{model_id}' not in /v1/models; using fallback '{fallback}'",
                }
            )
        else:
            # Critical failure if no fallback and model is missing.
            msg = f"  CRITICAL MISSING: {task} -> {model_id} - NO FALLBACK AVAILABLE"
            print(msg)
            findings.append(
                {
                    "finding": f"F-MODEL-{task.upper()}-CRITICAL",
                    "detail": f"D-18 starter '{model_id}' not in /v1/models and NO fallback is defined.",
                }
            )
            # Optionally exit here if this is deemed a hard block

if findings:
    print(
        f"\n[ALT-PICKED] {len(findings)} issue(s) found. Record in MODEL-EVALUATION-RESULTS.md."
    )


# ─── STEP B: Ranking tasks (5x) ───────────────────────────────────────────
sep("STEP B: RANKING TASKS (5 batches, 3-5 items each)")

RANKING_SETS = [
    [
        "OpenAI releases GPT-5.4 with 2x coding benchmark improvement",
        "Google DeepMind publishes Gemini 3 Flash Preview - 1M context, $0.075/1M tokens",
        "Cursor 1.0 ships with background agent and checkpoint rollback",
    ],
    [
        "Anthropic releases Claude Sonnet 4.6 with extended thinking mode",
        "Meta open-sources Llama 4 Scout: 17B-A3B MoE runs on consumer GPU",
        "Microsoft integrates GitHub Copilot directly into VS Code task runner",
        "Mistral releases Devstral: coding-specialized 24B open weights",
    ],
    [
        "OpenRouter adds batch inference API at 50% discount",
        "Ollama 0.7 adds multi-model concurrency on CPU",
        "LangChain releases LangGraph Studio with visual flow editor",
    ],
    [
        "Anthropic publishes safety paper on multi-agent coordination risks",
        "OpenAI o3 reasoning model now generally available at $2/1M tokens",
        "Google AI Studio adds project-level memory for Gemini Pro",
        "Hugging Face releases SmolLM3: 3B model beats 7B on coding tasks",
    ],
    [
        "New benchmark shows GPT-5 hallucinates 40% less than GPT-4o on tech facts",
        "Vercel AI SDK 4.0 adds streaming tool calls with automatic retry",
        "AWS Bedrock adds on-demand fine-tuning for Claude 3.5 Haiku",
    ],
]

ranking_results = []
for i, items in enumerate(RANKING_SETS, 1):
    numbered = "\n".join(f"{j + 1}. {item}" for j, item in enumerate(items))
    prompt = f"Rank these AI news items by importance for someone who builds AI-powered tools. Reply with ranked list (1=most important) and one sentence rationale per item:\n\n{numbered}"
    print(f"\n[Ranking {i}/{len(RANKING_SETS)}] {len(items)} items...")
    result = chat("ranking", prompt, model_override=effective_models["ranking"])
    result["task"] = f"ranking_{i}"
    result["input_items"] = items
    ranking_results.append(result)
    if result["status"] == "ok":
        print(
            f"  Latency: {result['latency_s']}s | Cost: ${result.get('cost_usd', 0):.5f}"
        )
        print(f"  Output (first 300 chars): {result['content'][:300]}")
    else:
        print(f"  ERROR: {result.get('error')}")


# ─── STEP C: Summarization tasks (5x) ────────────────────────────────────
sep("STEP C: SUMMARIZATION TASKS (5 snippets)")

SUMMARIZATION_INPUTS = [
    "OpenAI today announced GPT-5.4, the latest iteration of its flagship model. The new model demonstrates a 2x improvement on HumanEval and SWE-bench compared to GPT-4o, while reducing hallucination rates by approximately 40% on factual technology queries. Pricing is set at $5/1M input tokens and $20/1M output tokens via the API. GPT-5.4 is available immediately via ChatGPT Plus and the OpenAI API.",
    "Google DeepMind has released Gemini 3 Flash Preview, a long-context efficiency model supporting up to 1 million tokens. The model targets developer workloads requiring large-context reasoning at low cost, priced at $0.075 per million input tokens. Gemini 3 Flash Preview is available through Google AI Studio and Vertex AI with a 60 requests-per-minute free tier limit.",
    "Cursor today shipped version 1.0 of its AI-native code editor. The headline features include a background agent that executes multi-step coding tasks asynchronously, a checkpoint and rollback system for agentic changes, and a redesigned diff view. The background agent can run terminal commands, write files, and create pull requests without keeping the editor in focus.",
    "Meta released Llama 4 Scout under the Llama open license. Scout is a 17-billion active parameter mixture-of-experts model with 16 experts, totaling 109B parameters. It achieves competitive coding scores against models twice its active size and can run on a single consumer GPU with 24GB VRAM. The release includes fine-tuning recipes and model weights via the Llama website.",
    "Anthropic published new research on multi-agent coordination safety, describing attack patterns where subagent outputs can contain adversarial instructions that cause orchestrator agents to take unintended actions. The paper introduces a classification of trust levels for agent-to-agent communication and recommends that orchestrators treat subagent outputs as untrusted user input by default.",
]

summarization_results = []
for i, snippet in enumerate(SUMMARIZATION_INPUTS, 1):
    prompt = f"Summarize this AI news item in 2-3 sentences for a developer audience. Be concrete about what changed and what developers can do with it:\n\n{snippet}"
    print(f"\n[Summarization {i}/{len(SUMMARIZATION_INPUTS)}]...")
    result = chat(
        "summarization", prompt, model_override=effective_models["summarization"]
    )
    result["task"] = f"summarization_{i}"
    result["input_snippet"] = snippet[:80] + "..."
    summarization_results.append(result)
    if result["status"] == "ok":
        print(
            f"  Latency: {result['latency_s']}s | Cost: ${result.get('cost_usd', 0):.5f}"
        )
        print(f"  Output: {result['content'][:300]}")
    else:
        print(f"  ERROR: {result.get('error')}")


# ─── STEP D: Why-it-matters tasks (4x) ───────────────────────────────────
sep("STEP D: WHY-IT-MATTERS TASKS (4 headlines)")

WIM_INPUTS = [
    {
        "headline": "Cursor 1.0 ships background agent with checkpoint rollback",
        "paragraph": "Cursor's background agent executes multi-step coding tasks asynchronously without blocking the editor. It can write files, run terminal commands, and open pull requests. A checkpoint system lets users roll back agentic changes to any prior state.",
    },
    {
        "headline": "Meta open-sources Llama 4 Scout: 17B active params, runs on 24GB GPU",
        "paragraph": "Scout is a mixture-of-experts model with 16 experts (17B active / 109B total). It beats same-size dense models on coding benchmarks. Available for download and fine-tuning under the Llama license.",
    },
    {
        "headline": "Anthropic research: subagent outputs can hijack orchestrator agents",
        "paragraph": "Adversarial instructions embedded in tool outputs or subagent responses can cause orchestrator agents to execute unintended actions. The paper recommends orchestrators treat all subagent content as untrusted user input.",
    },
    {
        "headline": "OpenRouter adds batch inference API at 50% token discount",
        "paragraph": "Batch requests are queued and processed asynchronously with results available within 24 hours. Supported for all models. Pricing is 50% of standard synchronous rates, with a 10k request-per-batch limit.",
    },
]

wim_results = []
for i, item in enumerate(WIM_INPUTS, 1):
    prompt = f"Explain in 2 sentences why this matters for someone who builds AI-powered tools. Be specific about the practical implication:\n\nHeadline: {item['headline']}\n\n{item['paragraph']}"
    print(f"\n[Why-it-matters {i}/{len(WIM_INPUTS)}]...")
    result = chat(
        "why_it_matters", prompt, model_override=effective_models["why_it_matters"]
    )
    result["task"] = f"why_it_matters_{i}"
    result["headline"] = item["headline"]
    wim_results.append(result)
    if result["status"] == "ok":
        print(
            f"  Latency: {result['latency_s']}s | Cost: ${result.get('cost_usd', 0):.5f}"
        )
        print(f"  Output: {result['content'][:300]}")
    else:
        print(f"  ERROR: {result.get('error')}")


# ─── STEP E: Embedding endpoint test ──────────────────────────────────────
sep("STEP E: EMBEDDING ENDPOINT TEST")

print(f"\nTesting {effective_models['embedding']} on /v1/embeddings...")
embed_result = embed(
    "OpenAI released GPT-5.4 with improved coding benchmarks",
    model_override=effective_models["embedding"],
)

if embed_result["status"] == "ok":
    print(
        f"  PASS: dimensions={embed_result['dimensions']}, latency={embed_result['latency_s']}s"
    )
    print(f"  Sample vector (first 4 dims): {embed_result['sample']}")
else:
    print(
        f"  FAIL: {embed_result.get('http_status', '')} {embed_result.get('error', embed_result.get('body', ''))}"
    )
    # Try fallback 1
    print(f"\nTrying fallback 1: {FALLBACKS.get('embedding')}...")
    fallback1_model = FALLBACKS.get("embedding")
    if fallback1_model:
        embed_result2 = embed(
            "OpenAI released GPT-5.4 with improved coding benchmarks",
            model_override=fallback1_model,
        )
        if embed_result2["status"] == "ok":
            print(f"  FALLBACK 1 PASS: dimensions={embed_result2['dimensions']}")
            embed_result = embed_result2
            findings.append(
                {
                    "finding": "F-EMBED-FALLBACK1",
                    "detail": f"Primary embedding model '{MODELS['embedding']}' unavailable/failed on /v1/embeddings; using fallback '{fallback1_model}'",
                }
            )
            # Update models.yaml recommendation if this is the first successful fallback
            print(
                f"  ACTION REQUIRED: Update config/models.yaml embedding model to '{fallback1_model}' if this fallback is preferred."
            )
        else:
            print(
                f"  FALLBACK 1 FAIL: {embed_result2.get('http_status', '')} {embed_result2.get('error', embed_result2.get('body', ''))}"
            )
            # Try fallback 2
            print(f"\nTrying fallback 2: {EMBEDDING_FALLBACK_2}...")
            embed_result3 = embed(
                "OpenAI released GPT-5.4 with improved coding benchmarks",
                model_override=EMBEDDING_FALLBACK_2,
            )
            if embed_result3["status"] == "ok":
                print(f"  FALLBACK 2 PASS: dimensions={embed_result3['dimensions']}")
                embed_result = embed_result3
                findings.append(
                    {
                        "finding": "F-EMBED-FALLBACK2",
                        "detail": f"Primary and fallback 1 embedding models failed; using '{EMBEDDING_FALLBACK_2}'.",
                    }
                )
                print(
                    f"  ACTION REQUIRED: Update config/models.yaml embedding model to '{EMBEDDING_FALLBACK_2}' if this fallback is preferred."
                )
            else:
                print(
                    f"  ALL EMBEDDING FALLBACKS FAILED - escalate to separate embedding provider decision"
                )
                findings.append(
                    {
                        "finding": "F-EMBED-BLOCKED",
                        "detail": "All 3 embedding options failed on OpenRouter /v1/embeddings. Separate provider decision needed.",
                    }
                )
    else:
        # No fallback defined, report as critical
        print(
            f"  CRITICAL FAIL: Embedding model '{MODELS['embedding']}' failed and no fallback is defined."
        )
        findings.append(
            {
                "finding": "F-EMBED-CRITICAL",
                "detail": f"Primary embedding model '{MODELS['embedding']}' failed and no fallback is defined.",
            }
        )


# ─── STEP F: Summary ──────────────────────────────────────────────────────
sep("SUMMARY")

all_results = ranking_results + summarization_results + wim_results
ok_count = sum(1 for r in all_results if r["status"] == "ok")
err_count = len(all_results) - ok_count

print(f"Tasks completed: {ok_count}/{len(all_results)}")
print(f"Errors: {err_count}")
print(f"Cumulative OpenRouter spend: ${total_cost_usd:.5f} (cap: $20 / abort: $18)")
print(f"Findings: {len(findings)}")
for f in findings:
    print(f"  [{f['finding']}] {f['detail']}")

print(
    "\n[NEXT] Review outputs above and fill in quality judgment in 00-MODEL-EVALUATION-RESULTS.md"
)
sys.exit(0)  # Exit cleanly after printing summary
