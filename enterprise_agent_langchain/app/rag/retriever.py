from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


@dataclass(slots=True)
class SearchHit:
    text: str
    score: float


class KnowledgeBaseRetriever:
    """教学版轻量检索器。"""

    def __init__(self, chunks: list[str]) -> None:
        self._chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        self._chunk_tokens = [tokenize(chunk) for chunk in self._chunks]

    @classmethod
    def from_text_file(cls, path: Path) -> "KnowledgeBaseRetriever":
        content = path.read_text(encoding="utf-8")
        chunks = [line.strip() for line in content.splitlines() if line.strip()]
        return cls(chunks)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        hits: list[SearchHit] = []
        for chunk, chunk_tokens in zip(self._chunks, self._chunk_tokens, strict=True):
            score = self._score(query_tokens, chunk_tokens)
            if score > 0:
                hits.append(SearchHit(text=chunk, score=score))

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    @staticmethod
    def _score(query_tokens: list[str], chunk_tokens: list[str]) -> float:
        if not chunk_tokens:
            return 0.0
        overlap = len(set(query_tokens) & set(chunk_tokens))
        if overlap == 0:
            return 0.0
        return overlap / math.sqrt(len(set(chunk_tokens)))
