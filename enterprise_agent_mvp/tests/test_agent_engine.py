import unittest

from app.agent.engine import AgentEngine
from app.models import (
    AssistantResponse,
    CanonicalMessage,
    ToolRequest,
    ToolSpec,
)


class FakeProvider:
    """用于测试的假 provider。

    第一次调用时先要求搜索知识库，第二次调用时再给最终答案，
    用来验证 AgentEngine 会不会正确执行“模型 -> 工具 -> 模型”的闭环。
    """
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, *, system_prompt, messages, tools, temperature=0.0, max_tokens=800):
        self.calls += 1
        if self.calls == 1:
            return AssistantResponse(
                text="I should look up the password reset policy.",
                tool_requests=[
                    ToolRequest(
                        tool_call_id="tool_1",
                        name="search_knowledge_base",
                        arguments={"query": "password reset"},
                    )
                ],
                raw={"provider": "fake"},
            )
        return AssistantResponse(
            text="Password resets require identity verification and a reset link.",
            tool_requests=[],
            raw={"provider": "fake"},
        )


class AgentEngineTests(unittest.TestCase):
    def test_executes_tool_call_and_returns_final_answer(self) -> None:
        """验证 AgentEngine 会执行工具调用并返回最终答案。"""
        provider = FakeProvider()
        tool_specs = [
            ToolSpec(
                name="search_knowledge_base",
                description="Searches support docs.",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            )
        ]
        tool_functions = {
            "search_knowledge_base": lambda query: "Password resets require identity verification and a reset link."
        }
        engine = AgentEngine(
            provider=provider,
            tool_specs=tool_specs,
            tool_functions=tool_functions,
            system_prompt="You are a support agent.",
        )

        result = engine.run("How do I reset my password?")

        self.assertEqual(provider.calls, 2)
        self.assertIn("identity verification", result.final_text)
        self.assertEqual(result.messages[-1].role, "assistant")
        self.assertIn("reset link", result.messages[-1].content)


if __name__ == "__main__":
    unittest.main()
