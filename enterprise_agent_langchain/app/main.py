from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.db.ticket_repository import TicketRepository
from app.langchain_runtime.agent_service import LangChainAgentService
from app.rag.retriever import KnowledgeBaseRetriever
from app.schemas import ChatRequest, ManualTicketRequest


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "app" / "static"


def build_service(settings: Settings) -> tuple[LangChainAgentService, TicketRepository]:
    repository = TicketRepository(settings.db_path)
    retriever = KnowledgeBaseRetriever.from_text_file(settings.knowledge_base_path)
    service = LangChainAgentService(settings=settings, repository=repository, retriever=retriever)
    return service, repository


def create_app() -> FastAPI:
    settings = Settings.from_env(ROOT_DIR)
    service, repository = build_service(settings)

    app = FastAPI(title="Enterprise Knowledge Agent - LangChain Edition", version="0.1.0")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "provider": settings.provider_name,
            "model": settings.model,
            "stack": "langchain",
        }

    @app.post("/chat")
    def chat(payload: ChatRequest) -> dict:
        try:
            result = service.run(payload.question, payload.history)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"LangChain agent request failed: {exc}") from exc
        return {"answer": result.answer, "messages": result.messages}

    @app.post("/tickets")
    def create_ticket(payload: ManualTicketRequest) -> dict:
        ticket = repository.create_ticket(
            title=payload.title,
            issue=payload.issue,
            priority=payload.priority,
            customer_email=payload.customer_email,
        )
        return ticket.__dict__

    @app.get("/tickets")
    def list_tickets() -> list[dict]:
        return [ticket.__dict__ for ticket in repository.list_open_tickets()]

    @app.get("/tickets/{ticket_id}")
    def get_ticket(ticket_id: str) -> dict:
        ticket = repository.get_ticket(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail=f"Unknown ticket_id: {ticket_id}")
        return ticket.__dict__

    return app


app = create_app()

