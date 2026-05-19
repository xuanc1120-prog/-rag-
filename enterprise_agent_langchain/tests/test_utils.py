import unittest

from app.utils import normalize_history_payload, stringify_content


class UtilsTests(unittest.TestCase):
    def test_normalize_history_payload_filters_invalid_items(self) -> None:
        payload = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "tool", "content": "ignored"},
            {"role": "user", "content": ""},
        ]

        result = normalize_history_payload(payload)

        self.assertEqual(
            result,
            [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
            ],
        )

    def test_stringify_content_handles_non_string(self) -> None:
        text = stringify_content([{"type": "text", "text": "hello"}])
        self.assertIn("hello", text)


if __name__ == "__main__":
    unittest.main()

