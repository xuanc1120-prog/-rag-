from __future__ import annotations

import math
import re
from pathlib import Path

from app.models import SearchHit


# 这里只做非常轻量的英文分词，适合原型项目理解流程。
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    """把文本切成小写 token 列表。"""
    return TOKEN_PATTERN.findall(text.lower())


class KnowledgeBaseRetriever:
    """轻量知识库检索器。"""
    def __init__(self, chunks: list[str]) -> None:
        self._chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        self._chunk_tokens = [tokenize(chunk) for chunk in self._chunks]

    @classmethod
    def from_text_file(cls, path: Path) -> "KnowledgeBaseRetriever":
        """从纯文本文件按行加载知识库。"""
        content = path.read_text(encoding="utf-8")
        chunks = [line.strip() for line in content.splitlines() if line.strip()]
        return cls(chunks)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        """返回与查询最相关的若干知识片段。"""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored_hits: list[SearchHit] = []
        for chunk, chunk_tokens in zip(self._chunks, self._chunk_tokens, strict=True):
            score = self._score(query_tokens, chunk_tokens)
            if score > 0:
                scored_hits.append(SearchHit(text=chunk, score=score))

        scored_hits.sort(key=lambda hit: hit.score, reverse=True)
        return scored_hits[:top_k]

    @staticmethod
    def _score(query_tokens: list[str], chunk_tokens: list[str]) -> float:
        """计算查询和知识片段之间的简单相关度分数。"""
        if not chunk_tokens:
            return 0.0
        overlap = len(set(query_tokens) & set(chunk_tokens))
        if overlap == 0:
            return 0.0
        return overlap / math.sqrt(len(set(chunk_tokens)))
