import yaml
from pathlib import Path
from typing import Any

class ConfigError(Exception):
    """Raised when configuration is missing or malformed."""
    pass

def load_sources() -> list[dict[str, Any]]:
    """Load curated AI news watchlist from config/sources.yaml."""
    path = Path("config/sources.yaml")
    if not path.exists():
        raise ConfigError(f"Sources file not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("sources", [])
    except Exception as e:
        raise ConfigError(f"Failed to load sources: {e}")

def load_models() -> dict[str, str]:
    """Load model mapping from config/models.yaml."""
    path = Path("config/models.yaml")
    if not path.exists():
        raise ConfigError(f"Models file not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            tasks = data.get("tasks", {})
            return {k: v["model"] for k, v in tasks.items()}
    except Exception as e:
        raise ConfigError(f"Failed to load models: {e}")

def load_openrouter_key() -> str:
    """Load OpenRouter API key from config/microclaw.config.yaml."""
    path = Path("config/microclaw.config.yaml")
    if not path.exists():
        raise ConfigError(f"Secret config not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            key = data.get("openrouter_api_key", "").strip()
            if not key:
                raise ConfigError("openrouter_api_key missing or empty in microclaw.config.yaml")
            return key
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load OpenRouter key: {e}")
