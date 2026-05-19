import unittest

from app.providers.anthropic_provider import AnthropicProvider
from app.providers.openai_compatible import OpenAICompatibleProvider


class ProviderNormalizationTests(unittest.TestCase):
    def test_openai_compatible_provider_extracts_text_and_tool_calls(self) -> None:
        """验证 OpenAI 风格响应能被正确拆成文本和工具调用。"""
        payload = {
            "choices": [
                {
                    "message": {
                        "content": "I can create a ticket for this issue.",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "create_ticket",
                                    "arguments": '{"title":"Password reset","issue":"User is blocked","priority":"medium","customer_email":"user@example.com"}',
                                },
                            }
                        ],
                    }
                }
            ]
        }

        result = OpenAICompatibleProvider.normalize_response(payload)

        self.assertEqual(result.text, "I can create a ticket for this issue.")
        self.assertEqual(result.tool_requests[0].name, "create_ticket")
        self.assertEqual(result.tool_requests[0].arguments["priority"], "medium")

    def test_anthropic_provider_extracts_text_and_tool_calls(self) -> None:
        """验证 Anthropic 风格 content blocks 也能被统一抽取。"""
        payload = {
            "content": [
                {"type": "text", "text": "I need to search the knowledge base first."},
                {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "search_knowledge_base",
                    "input": {"query": "password reset"},
                },
            ]
        }

        result = AnthropicProvider.normalize_response(payload)

        self.assertEqual(result.text, "I need to search the knowledge base first.")
        self.assertEqual(result.tool_requests[0].name, "search_knowledge_base")
        self.assertEqual(result.tool_requests[0].arguments["query"], "password reset")


if __name__ == "__main__":
    unittest.main()
