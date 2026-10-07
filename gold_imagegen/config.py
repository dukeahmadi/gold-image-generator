from __future__ import annotations

import os

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Required configuration is missing."""


def openrouter_api_key() -> str:
    load_dotenv()
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise ConfigError(
            "OPENROUTER_API_KEY is not set. Put it in .env (see .env.example) "
            "or export it in your shell. Never commit it."
        )
    return key
