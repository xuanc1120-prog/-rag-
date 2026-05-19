from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib import request

from app.models import AssistantResponse, CanonicalMessage, ToolRequest, ToolSpec
from app.providers.base import LLMProvider, ProviderError


class AnthropicProvider(LLMProvider):
    """对接 Anthropic 风格 messages 接口的 provider。"""
    def __init__(self, *, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def normalize_response(payload: dict) -> AssistantResponse:
        """把 Anthropic 风格 content blocks 整理成内部统一格式。"""
        tool_requests: list[ToolRequest] = []
        text_parts: list[str] = []
        for block in payload.get("content", []):
            if block["type"] == "text":
                text_parts.append(block.get("text", ""))
            if block["type"] == "tool_use":
                tool_requests.append(
                    ToolRequest(
                        tool_call_id=block["id"],
                        name=block["name"],
                        arguments=block.get("input", {}),
                    )
                )
        return AssistantResponse(text="".join(text_parts).strip(), tool_requests=tool_requests, raw=payload)

    def generate(
        self,
        *,
        system_prompt: str,
        messages: list[CanonicalMessage],
        tools: list[ToolSpec],
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> AssistantResponse:
        """发起一次 Anthropic 风格接口调用。"""
        payload = {
            "model": self.model,
            "system": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # Anthropic 风格接口把 system prompt 单独放在 system 字段。
            "messages": self._build_messages(messages),
            "tools": self._build_tools(tools),
        }
        http_request = request.Request(
            url=f"{self.base_url}/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=60) as response:
                raw = json.loads(response.read().decode("utf-8"))
            return self.normalize_response(raw)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"Anthropic provider request failed: {exc}") from exc

    @staticmethod
    def _build_messages(messages: list[CanonicalMessage]) -> list[dict]:
        """把内部消息格式转换成 Anthropic content blocks。"""
        built_messages: list[dict] = []
        for message in messages:
            if message.role == "user":
                built_messages.append({"role": "user", "content": [{"type": "text", "text": message.content}]})
            elif message.role == "assistant":
                content_blocks: list[dict] = []
                if message.content:
                    content_blocks.append({"type": "text", "text": message.content})
                for tool_call in message.tool_calls:
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tool_call.tool_call_id,
                            "name": tool_call.name,
                            "input": tool_call.arguments,
                        }
                    )
                built_messages.append({"role": "assistant", "content": content_blocks})
            elif message.role == "tool":
                built_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": message.tool_call_id,
                                "content": message.content,
                            }
                        ],
                    }
                )
        return built_messages

    @staticmethod
    def _build_tools(tools: list[ToolSpec]) -> list[dict]:
        """把内部工具描述转成 Anthropic tool schema。"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]
