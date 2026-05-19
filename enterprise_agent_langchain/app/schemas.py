from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Current user question.")
    history: list[dict[str, str]] = Field(default_factory=list, description="Prior user/assistant turns.")


class ManualTicketRequest(BaseModel):
    title: str
    issue: str
    priority: str = "medium"
    customer_email: str

