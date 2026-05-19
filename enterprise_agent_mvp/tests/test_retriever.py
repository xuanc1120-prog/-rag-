from pathlib import Path
import tempfile
import unittest

from app.rag.retriever import KnowledgeBaseRetriever


class KnowledgeBaseRetrieverTests(unittest.TestCase):
    def test_returns_most_relevant_chunk_for_password_reset_query(self) -> None:
        """验证检索器能把最相关的密码重置知识排到前面。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            kb_path = Path(tmp_dir) / "kb.txt"
            kb_path.write_text(
                "\n".join(
                    [
                        "Password resets require identity verification and a reset link.",
                        "VPN issues should be routed to the network team.",
                        "Refund requests require order id and account email.",
                    ]
                ),
                encoding="utf-8",
            )

            retriever = KnowledgeBaseRetriever.from_text_file(kb_path)

            results = retriever.search("How do I reset my password?", top_k=2)

            self.assertGreaterEqual(len(results), 1)
            self.assertIn("Password resets", results[0].text)


if __name__ == "__main__":
    unittest.main()
