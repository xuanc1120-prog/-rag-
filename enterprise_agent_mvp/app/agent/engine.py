from __future__ import annotations

from typing import Callable

from app.models import AgentRunResult, CanonicalMessage, ToolSpec
from app.providers.base import LLMProvider


class AgentEngine:
    """Agent 主循环。

    它的职责很单纯：
    1. 把当前消息列表交给模型
    2. 看模型是否想调用工具
    3. 如果要调用，就执行工具并把结果塞回消息列表
    4. 重复直到模型不再调工具，或者达到最大轮数
    """
    def __init__(
        self,
        *,
        provider: LLMProvider,
        tool_specs: list[ToolSpec],
        tool_functions: dict[str, Callable[..., str]],
        system_prompt: str,
        max_turns: int = 4,
    ) -> None:
        self.provider = provider
        self.tool_specs = tool_specs
        self.tool_functions = tool_functions
        self.system_prompt = system_prompt
        self.max_turns = max_turns

    def run(self, user_input: str, history: list[CanonicalMessage] | None = None) -> AgentRunResult:
        """执行一次完整的 Agent 运行。"""
        # 先把历史消息复制一份，避免原始输入在运行中被修改。
        messages = list(history or [])
        messages.append(CanonicalMessage(role="user", content=user_input))

        final_text = ""
        for _ in range(self.max_turns):
            # 每一轮都把当前完整上下文发给模型，让模型决定是直接回答还是先用工具。
            response = self.provider.generate(
                system_prompt=self.system_prompt,
                messages=messages,
                tools=self.tool_specs,
            )
            messages.append(
                CanonicalMessage(
                    role="assistant",
                    content=response.text,
                    tool_calls=response.tool_requests,
                )
            )
            final_text = response.text

            if not response.tool_requests:
                # 没有工具调用时，说明模型已经给出了最终答案。
                return AgentRunResult(final_text=final_text, messages=messages)

            for tool_request in response.tool_requests:
                # 根据模型返回的工具名，找到本地真正执行的函数。
                tool = self.tool_functions.get(tool_request.name)
                if tool is None:
                    result = f"Unknown tool: {tool_request.name}"
                else:
                    result = tool(**tool_request.arguments)
                messages.append(
                    CanonicalMessage(
                        role="tool",
                        content=result,
                        tool_call_id=tool_request.tool_call_id,
                        name=tool_request.name,
                    )
                )

        # 如果到达最大轮数还没自然结束，就返回当前已有的最好结果。
        return AgentRunResult(final_text=final_text, messages=messages)
