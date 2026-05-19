from __future__ import annotations

from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import LLMProvider
from app.providers.openai_compatible import OpenAICompatibleProvider


def create_provider(*, provider_name: str, model: str, api_key: str, base_url: str) -> LLMProvider:
    """根据配置创建对应的 provider 实例。"""
    normalized_name = provider_name.strip().lower()
    if normalized_name == "openai_compatible":
        return OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url)
    if normalized_name == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model, base_url=base_url)
    raise ValueError(f"Unsupported provider: {provider_name}")
