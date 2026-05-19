from __future__ import annotations

import json
from typing import Callable

from app.db.ticket_repository import TicketRepository
from app.models import ToolSpec
from app.rag.retriever import KnowledgeBaseRetriever


def build_tool_specs() -> list[ToolSpec]:
    """定义提供给模型调用的工具清单。"""
    return [
        ToolSpec(
            name="search_knowledge_base",
            description="Searches the internal support knowledge base for relevant troubleshooting steps.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The issue or question to search for."}
                },
                "required": ["query"],
            },
        ),
        ToolSpec(
            name="create_ticket",
            description="Creates a support ticket when the issue needs manual follow-up.",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "issue": {"type": "string"},
                    "priority": {"type": "string"},
                    "customer_email": {"type": "string"},
                },
                "required": ["title", "issue", "priority", "customer_email"],
            },
        ),
        ToolSpec(
            name="get_ticket",
            description="Fetches the current state of an existing support ticket.",
            input_schema={
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": ["ticket_id"],
            },
        ),
        ToolSpec(
            name="escalate_ticket",
            description="Escalates an existing ticket and raises its priority.",
            input_schema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["ticket_id", "reason"],
            },
        ),
    ]


def build_tool_functions(
    *,
    repository: TicketRepository,
    retriever: KnowledgeBaseRetriever,
) -> dict[str, Callable[..., str]]:
    """返回真正执行工具动作的函数映射表。"""
    def search_knowledge_base(query: str) -> str:
        # 工具返回值统一转成 JSON 字符串，便于模型读取结构化结果。
        hits = retriever.search(query, top_k=3)
        payload = [{"text": hit.text, "score": round(hit.score, 3)} for hit in hits]
        return json.dumps({"results": payload}, ensure_ascii=False)

    def create_ticket(title: str, issue: str, priority: str, customer_email: str) -> str:
        ticket = repository.create_ticket(
            title=title,
            issue=issue,
            priority=priority,
            customer_email=customer_email,
        )
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    def get_ticket(ticket_id: str) -> str:
        ticket = repository.get_ticket(ticket_id)
        if ticket is None:
            return json.dumps({"error": f"Unknown ticket_id: {ticket_id}"}, ensure_ascii=False)
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    def escalate_ticket(ticket_id: str, reason: str) -> str:
        try:
            ticket = repository.escalate_ticket(ticket_id, reason)
        except KeyError as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    return {
        "search_knowledge_base": search_knowledge_base,
        "create_ticket": create_ticket,
        "get_ticket": get_ticket,
        "escalate_ticket": escalate_ticket,
    }
