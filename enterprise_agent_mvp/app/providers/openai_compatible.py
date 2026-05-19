from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib import request

from app.models import AssistantResponse, CanonicalMessage, ToolRequest, ToolSpec
from app.providers.base import LLMProvider, ProviderError


class OpenAICompatibleProvider(LLMProvider):
    """对接 OpenAI 风格聊天接口的 provider。"""
    def __init__(self, *, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def normalize_response(payload: dict) -> AssistantResponse:
        """把 OpenAI 风格返回结果整理成内部统一格式。"""
        message = payload["choices"][0]["message"]
        text = message.get("content") or ""
        tool_requests: list[ToolRequest] = []
        for tool_call in message.get("tool_calls", []):
            raw_args = tool_call.get("function", {}).get("arguments", "{}")
            arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            tool_requests.append(
                ToolRequest(
                    tool_call_id=tool_call["id"],
                    name=tool_call["function"]["name"],
                    arguments=arguments,
                )
            )
        return AssistantResponse(text=text, tool_requests=tool_requests, raw=payload)

    def generate(
        self,
        *,
        system_prompt: str,
        messages: list[CanonicalMessage],
        tools: list[ToolSpec],
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> AssistantResponse:
        """发起一次 OpenAI 兼容接口调用。"""
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # OpenAI 风格接口要求 system prompt 混在 messages 数组里。
            "messages": self._build_messages(system_prompt, messages),
            "tools": self._build_tools(tools),
            "tool_choice": "auto",
        }
        http_request = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=60) as response:
                raw = json.loads(response.read().decode("utf-8"))
            return self.normalize_response(raw)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"OpenAI-compatible provider request failed: {exc}") from exc

    @staticmethod
    def _build_messages(system_prompt: str, messages: list[CanonicalMessage]) -> list[dict]:
        """把内部消息格式转换成 OpenAI 接口需要的 messages。"""
        built_messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for message in messages:
            if message.role == "assistant" and message.tool_calls:
                built_messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": json.dumps(tool_call.arguments, ensure_ascii=False),
                                },
                            }
                            for tool_call in message.tool_calls
                        ],
                    }
                )
            elif message.role == "tool":
                built_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": message.tool_call_id,
                        "name": message.name,
                        "content": message.content,
                    }
                )
            else:
                built_messages.append({"role": message.role, "content": message.content})
        return built_messages

    @staticmethod
    def _build_tools(tools: list[ToolSpec]) -> list[dict]:
        """把内部工具描述转成 OpenAI function calling 所需结构。"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]
