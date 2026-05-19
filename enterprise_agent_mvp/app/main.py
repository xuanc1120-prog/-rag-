from __future__ import annotations

from pathlib import Path

from app.agent.engine import AgentEngine
from app.config import Settings
from app.db.ticket_repository import TicketRepository
from app.models import CanonicalMessage
from app.providers.base import ProviderError
from app.providers.factory import create_provider
from app.rag.retriever import KnowledgeBaseRetriever
from app.tools.ticket_tools import build_tool_functions, build_tool_specs

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover - runtime-only dependency
    FastAPI = None
    HTTPException = RuntimeError
    FileResponse = RuntimeError
    StaticFiles = RuntimeError
    BaseModel = object
    Field = lambda default=None, **_: default


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "app" / "static"


class ChatRequest(BaseModel):
    """聊天接口的请求体。"""
    question: str = Field(..., min_length=1, description="The support question from the user.")
    history: list[dict[str, str]] = Field(default_factory=list, description="Optional prior messages for multi-turn chat.")


class ManualTicketRequest(BaseModel):
    """手动创建工单接口的请求体。"""
    title: str
    issue: str
    priority: str = "medium"
    customer_email: str


def build_history_messages(history_payload: list[dict[str, str]] | None) -> list[CanonicalMessage]:
    """把接口层收到的 history JSON 转成内部统一消息格式。"""
    messages: list[CanonicalMessage] = []
    for item in history_payload or []:
        role = item.get("role", "").strip()
        content = item.get("content", "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append(CanonicalMessage(role=role, content=content))
    return messages


def build_engine(settings: Settings) -> tuple[AgentEngine, TicketRepository]:
    """按配置组装整个 Agent 运行环境。"""
    # 仓库、检索器、provider、tools 在这里统一接线，避免 API 层知道太多细节。
    repository = TicketRepository(settings.db_path)
    retriever = KnowledgeBaseRetriever.from_text_file(settings.knowledge_base_path)
    provider = create_provider(
        provider_name=settings.provider_name,
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
    tool_specs = build_tool_specs()
    tool_functions = build_tool_functions(repository=repository, retriever=retriever)
    engine = AgentEngine(
        provider=provider,
        tool_specs=tool_specs,
        tool_functions=tool_functions,
        system_prompt=settings.system_prompt,
        max_turns=settings.max_turns,
    )
    return engine, repository


def create_app() -> "FastAPI":
    """创建 FastAPI 应用实例。"""
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI is not installed. Run `pip install -r requirements.txt` before starting the API server."
        )

    settings = Settings.from_env(ROOT_DIR)
    engine, repository = build_engine(settings)
    app = FastAPI(title="Enterprise Knowledge Agent MVP", version="0.1.0")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index() -> "FileResponse":
        """返回前端主页。"""
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        """返回当前服务状态以及正在使用的 provider / model。"""
        return {"status": "ok", "provider": settings.provider_name, "model": settings.model}

    @app.post("/chat")
    def chat(payload: ChatRequest) -> dict:
        """聊天主接口。"""
        try:
            result = engine.run(payload.question, history=build_history_messages(payload.history))
        except ProviderError as exc:
            # 本地服务可用、但上游模型接口失败时，对外统一返回 502。
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "answer": result.final_text,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [
                        {"id": tool.tool_call_id, "name": tool.name, "arguments": tool.arguments}
                        for tool in message.tool_calls
                    ],
                    "tool_call_id": message.tool_call_id,
                    "name": message.name,
                }
                for message in result.messages
            ],
        }

    @app.post("/tickets")
    def create_manual_ticket(payload: ManualTicketRequest) -> dict:
        """绕过 Agent，直接手动创建工单。"""
        ticket = repository.create_ticket(
            title=payload.title,
            issue=payload.issue,
            priority=payload.priority,
            customer_email=payload.customer_email,
        )
        return ticket.__dict__

    @app.get("/tickets")
    def list_tickets() -> list[dict]:
        """返回所有未关闭工单，方便前端展示。"""
        return [ticket.__dict__ for ticket in repository.list_open_tickets()]

    @app.get("/tickets/{ticket_id}")
    def get_ticket(ticket_id: str) -> dict:
        """按工单号查询工单。"""
        ticket = repository.get_ticket(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail=f"Unknown ticket_id: {ticket_id}")
        return ticket.__dict__

    return app


app = create_app() if FastAPI is not None else None
