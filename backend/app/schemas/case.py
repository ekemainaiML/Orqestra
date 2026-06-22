import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class CaseResponse(BaseModel):
    id: str
    customer_id: str
    request_text: str
    status: str
    iteration: int
    workflow_type: str
    confidence: float | None = None
    completeness: float | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class CaseCreate(BaseModel):
    customer_id: uuid.UUID
    request_text: str
    workflow_type: str = "order_fulfillment"

    @field_validator("request_text")
    @classmethod
    def request_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("request_text must not be empty")
        return v


class CaseDetail(CaseResponse):
    events: list[dict[str, Any]] = []
    directives: list[dict[str, Any]] = []


class GovernanceAction(BaseModel):
    action: str
    directive: dict[str, Any] | None = None
