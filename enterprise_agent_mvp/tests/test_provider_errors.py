import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from app.models import CanonicalMessage, ToolSpec
from app.providers.base import ProviderError
from app.providers.openai_compatible import OpenAICompatibleProvider


class ProviderErrorTests(unittest.TestCase):
    def test_openai_provider_wraps_http_failures(self) -> None:
        """验证上游 HTTP 错误会被包装成统一的 ProviderError。"""
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            model="test-model",
            base_url="https://example.com/v1",
        )

        with patch("app.providers.openai_compatible.request.urlopen") as mocked_urlopen:
            mocked_urlopen.side_effect = HTTPError(
                url="https://example.com/v1/chat/completions",
                code=401,
                msg="Unauthorized",
                hdrs=None,
                fp=None,
            )

            with self.assertRaises(ProviderError):
                provider.generate(
                    system_prompt="You are a support agent.",
                    messages=[CanonicalMessage(role="user", content="hello")],
                    tools=[
                        ToolSpec(
                            name="search_knowledge_base",
                            description="Searches docs",
                            input_schema={"type": "object", "properties": {}, "required": []},
                        )
                    ],
                )


if __name__ == "__main__":
    unittest.main()
