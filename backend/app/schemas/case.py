from datetime import datetime
from typing import Any

from pydantic import BaseModel


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
    customer_id: str
    request_text: str
    workflow_type: str = "order_fulfillment"


class CaseDetail(CaseResponse):
    events: list[dict[str, Any]] = []
    directives: list[dict[str, Any]] = []


class GovernanceAction(BaseModel):
    action: str
    directive: dict[str, Any] | None = None
