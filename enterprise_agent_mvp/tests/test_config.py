import os
import tempfile
import unittest
from pathlib import Path

from app.config import Settings


class SettingsTests(unittest.TestCase):
    def test_loads_values_from_dotenv_file(self) -> None:
        """验证 Settings 能正确读取临时 .env 文件。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "LLM_PROVIDER=anthropic",
                        "ANTHROPIC_API_KEY=test-anthropic-key",
                        "ANTHROPIC_MODEL=claude-test",
                        "MAX_AGENT_TURNS=6",
                    ]
                ),
                encoding="utf-8",
            )
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "knowledge_base.txt").write_text("Test knowledge.", encoding="utf-8")

            previous = os.environ.copy()
            try:
                for key in list(os.environ):
                    if key.startswith("OPENAI") or key.startswith("ANTHROPIC") or key in {
                        "LLM_PROVIDER",
                        "MAX_AGENT_TURNS",
                    }:
                        os.environ.pop(key, None)
                settings = Settings.from_env(root)
            finally:
                os.environ.clear()
                os.environ.update(previous)

            self.assertEqual(settings.provider_name, "anthropic")
            self.assertEqual(settings.api_key, "test-anthropic-key")
            self.assertEqual(settings.model, "claude-test")
            self.assertEqual(settings.max_turns, 6)


if __name__ == "__main__":
    unittest.main()
