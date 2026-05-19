from __future__ import annotations

import json

from app.db.ticket_repository import TicketRepository
from app.rag.retriever import KnowledgeBaseRetriever


def build_support_tools(*, repository: TicketRepository, retriever: KnowledgeBaseRetriever) -> list:
    """构建 LangChain 工具列表。"""
    from langchain.tools import tool

    @tool
    def search_knowledge_base(query: str) -> str:
        """搜索内部支持知识库，返回最相关的排障建议。"""
        hits = retriever.search(query, top_k=3)
        payload = [{"text": hit.text, "score": round(hit.score, 3)} for hit in hits]
        return json.dumps({"results": payload}, ensure_ascii=False)

    @tool
    def create_ticket(title: str, issue: str, priority: str, customer_email: str) -> str:
        """在问题无法自动解决时创建工单。"""
        ticket = repository.create_ticket(
            title=title,
            issue=issue,
            priority=priority,
            customer_email=customer_email,
        )
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    @tool
    def get_ticket(ticket_id: str) -> str:
        """查询已有工单的当前状态。"""
        ticket = repository.get_ticket(ticket_id)
        if ticket is None:
            return json.dumps({"error": f"Unknown ticket_id: {ticket_id}"}, ensure_ascii=False)
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    @tool
    def escalate_ticket(ticket_id: str, reason: str) -> str:
        """升级已有工单，并提升优先级。"""
        try:
            ticket = repository.escalate_ticket(ticket_id, reason)
        except KeyError as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)
        return json.dumps(ticket.__dict__, ensure_ascii=False)

    return [search_knowledge_base, create_ticket, get_ticket, escalate_ticket]

