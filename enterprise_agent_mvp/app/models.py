from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """返回不带微秒的 UTC ISO 时间字符串，方便数据库和接口统一使用。"""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class ToolRequest:
    """模型发起的一次工具调用请求。"""
    tool_call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(slots=True)
class ToolSpec:
    """暴露给模型的工具描述。"""
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(slots=True)
class AssistantResponse:
    """Provider 归一化后的模型回复。"""
    text: str
    tool_requests: list[ToolRequest]
    raw: dict[str, Any]


@dataclass(slots=True)
class CanonicalMessage:
    """项目内部统一使用的消息格式。"""
    role: str
    content: str
    tool_calls: list[ToolRequest] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None


@dataclass(slots=True)
class AgentRunResult:
    """一次 Agent 运行的最终结果。"""
    final_text: str
    messages: list[CanonicalMessage]


@dataclass(slots=True)
class SearchHit:
    """知识检索命中的单条结果。"""
    text: str
    score: float


@dataclass(slots=True)
class Ticket:
    """工单实体。"""
    ticket_id: str
    title: str
    issue: str
    priority: str
    status: str
    customer_email: str
    created_at: str
    updated_at: str
    resolution_notes: str = ""
