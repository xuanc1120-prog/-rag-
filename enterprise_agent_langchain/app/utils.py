from __future__ import annotations

import json
from typing import Any


def extract_text_from_content_blocks(content: Any) -> str:
    """从 Anthropic/LangChain 的 content blocks 中提取可展示文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if text:
                    text_parts.append(str(text))
        if text_parts:
            return "\n".join(text_parts).strip()
    return ""


def stringify_content(content: Any) -> str:
    """把 LangChain message content 统一转换成字符串。"""
    extracted = extract_text_from_content_blocks(content)
    if extracted:
        return extracted
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)


def normalize_history_payload(history_payload: list[dict[str, str]] | None) -> list[dict[str, str]]:
    """过滤前端传来的 history，只保留合法的 user / assistant 纯文本消息。"""
    normalized: list[dict[str, str]] = []
    for item in history_payload or []:
        role = item.get("role", "").strip()
        content = item.get("content", "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        normalized.append({"role": role, "content": content})
    return normalized
