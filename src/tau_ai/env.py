"""Environment-based provider configuration helpers."""

from dataclasses import dataclass
from os import environ

DEFAULT_OPENAI_COMPATIBLE_BASE_URL = "https://api.openai.com/v1"


@dataclass(frozen=True, slots=True)
class OpenAICompatibleConfig:
    """Configuration for an OpenAI-compatible chat completions endpoint."""

    api_key: str
    base_url: str = DEFAULT_OPENAI_COMPATIBLE_BASE_URL


def openai_compatible_config_from_env(
    *,
    api_key_var: str = "OPENAI_API_KEY",
    base_url_var: str = "OPENAI_BASE_URL",
) -> OpenAICompatibleConfig:
    """Load OpenAI-compatible provider configuration from environment variables."""
    api_key = environ.get(api_key_var)
    if not api_key:
        msg = f"Missing required environment variable: {api_key_var}"
        raise RuntimeError(msg)

    return OpenAICompatibleConfig(
        api_key=api_key,
        base_url=environ.get(base_url_var, DEFAULT_OPENAI_COMPATIBLE_BASE_URL).rstrip("/"),
    )
