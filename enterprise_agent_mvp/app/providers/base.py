from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import AssistantResponse, CanonicalMessage, ToolSpec


class ProviderError(RuntimeError):
    """Provider 请求或解析失败时抛出的统一异常。"""


class LLMProvider(ABC):
    """所有模型提供方都必须实现的最小接口。"""
    @abstractmethod
    def generate(
        self,
        *,
        system_prompt: str,
        messages: list[CanonicalMessage],
        tools: list[ToolSpec],
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> AssistantResponse:
        """生成一次模型回复，并归一化成统一内部格式。"""
        raise NotImplementedError
