from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import Settings
from app.db.ticket_repository import TicketRepository
from app.langchain_runtime.model_factory import create_chat_model
from app.rag.retriever import KnowledgeBaseRetriever
from app.tools.support_tools import build_support_tools
from app.utils import extract_text_from_content_blocks, normalize_history_payload, stringify_content


@dataclass(slots=True)
class AgentRunResult:
    answer: str
    messages: list[dict[str, Any]]


class LangChainAgentService:
    """用 LangChain create_agent 封装的支持 Agent。"""

    def __init__(self, *, settings: Settings, repository: TicketRepository, retriever: KnowledgeBaseRetriever) -> None:
        from langchain.agents import create_agent

        self.settings = settings
        self.repository = repository
        self.retriever = retriever
        self.tools = build_support_tools(repository=repository, retriever=retriever)
        self.model = create_chat_model(settings)
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=settings.system_prompt,
        )

    def run(self, question: str, history_payload: list[dict[str, str]] | None = None) -> AgentRunResult:
        """执行一次 Agent 调用。"""
        from langchain_core.messages import AIMessage, HumanMessage

        history = normalize_history_payload(history_payload)
        messages: list[Any] = []
        for item in history:
            if item["role"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            else:
                messages.append(AIMessage(content=item["content"]))
        messages.append(HumanMessage(content=question))

        # create_agent 返回的是 LangGraph 风格状态字典，messages 是最重要的轨迹。
        result = self.agent.invoke(
            {"messages": messages},
            config={"recursion_limit": max(10, self.settings.max_turns * 3)},
        )
        raw_messages = result.get("messages", [])
        serialized = [self._serialize_message(message) for message in raw_messages]
        answer = self._extract_final_answer(serialized)
        return AgentRunResult(answer=answer, messages=serialized)

    @staticmethod
    def _serialize_message(message: Any) -> dict[str, Any]:
        """把 LangChain message 对象转成前端易消费的结构。"""
        role = "assistant"
        message_type = getattr(message, "type", "")
        if message_type in {"human", "user"}:
            role = "user"
        elif message_type == "tool":
            role = "tool"
        elif message_type == "system":
            role = "system"

        tool_calls = []
        for tool_call in getattr(message, "tool_calls", []) or []:
            tool_calls.append(
                {
                    "id": tool_call.get("id"),
                    "name": tool_call.get("name"),
                    "arguments": tool_call.get("args", {}),
                }
            )

        return {
            "role": role,
            "content": stringify_content(getattr(message, "content", "")),
            "tool_calls": tool_calls,
            "tool_call_id": getattr(message, "tool_call_id", None),
            "name": getattr(message, "name", None),
            "type": message_type,
        }

    @staticmethod
    def _extract_final_answer(messages: list[dict[str, Any]]) -> str:
        """从轨迹中取最后一条 assistant 消息作为最终回答。"""
        for message in reversed(messages):
            if message["role"] == "assistant" and message["content"]:
                text = extract_text_from_content_blocks(message["content"])
                if text:
                    return text
                return message["content"]
        return ""
