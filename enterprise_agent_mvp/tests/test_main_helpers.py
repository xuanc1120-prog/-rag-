import unittest

from app.main import build_history_messages
from app.models import CanonicalMessage


class MainHelperTests(unittest.TestCase):
    def test_build_history_messages_supports_multi_turn_input(self) -> None:
        """验证接口层传入的 history 能被转换成内部消息格式。"""
        history_payload = [
            {"role": "user", "content": "I cannot log in."},
            {"role": "assistant", "content": "Please try resetting the password."},
            {"role": "user", "content": "That failed, help me escalate this."},
        ]

        messages = build_history_messages(history_payload)

        self.assertEqual(
            messages,
            [
                CanonicalMessage(role="user", content="I cannot log in."),
                CanonicalMessage(role="assistant", content="Please try resetting the password."),
                CanonicalMessage(role="user", content="That failed, help me escalate this."),
            ],
        )


if __name__ == "__main__":
    unittest.main()
