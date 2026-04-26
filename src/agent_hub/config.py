import os
import re
import yaml
from pathlib import Path
from typing import Any

class ConfigError(Exception):
    """Raised when configuration is missing or malformed."""
    pass

def _expand(value: str) -> str:
    """Expand ${VAR} references using environment variables."""
    return re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), ""), str(value))

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
            key = _expand(data.get("openrouter_api_key", "")).strip()
            if not key:
                raise ConfigError("openrouter_api_key missing or empty in microclaw.config.yaml")
            return key
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load OpenRouter key: {e}")


def load_discord_config() -> tuple[str, str]:
    """Return (bot_token, channel_id) from config/microclaw.config.yaml.

    bot_token is at: channels.discord.accounts.main.bot_token
    channel_id is at: channels.discord.channel_id
    """
    path = Path("config/microclaw.config.yaml")
    if not path.exists():
        raise ConfigError(f"Secret config not found: {path.absolute()}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            token = _expand(data["channels"]["discord"]["accounts"]["main"]["bot_token"]).strip()
            if not token:
                raise ConfigError("channels.discord.accounts.main.bot_token missing in microclaw.config.yaml")
            channel_id = _expand(data["channels"]["discord"].get("channel_id", "")).strip()
            if not channel_id:
                raise ConfigError("channels.discord.channel_id missing in microclaw.config.yaml")
            return token, channel_id
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Failed to load Discord config: {e}")
