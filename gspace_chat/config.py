"""Configuration helpers for environment-driven settings."""

from dataclasses import dataclass
import os


SEED_URLS = [
    "https://www.gspace.com/",
    "https://www.gspace.com/about",
    "https://www.gspace.com/team",
    "https://www.gspace.com/launch",
    "https://www.gspace.com/satellites",
    "https://www.gspace.com/career",
    "https://www.gspace.com/stem",
    "https://www.gspace.com/update",
    "https://www.gspace.com/asmn",
    "https://www.gspace.com/contact",
]


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )


def get_settings() -> Settings:
    """Return current settings.

    TODO: Add validation and required-field checks.
    """

    return Settings()
