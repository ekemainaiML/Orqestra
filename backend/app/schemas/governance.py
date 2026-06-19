from typing import Any

from pydantic import BaseModel


class BriefResponse(BaseModel):
    case_id: str
    customer_name: str
    request_summary: str
    status: str
    iteration: int
    recommended_strategy: str
    rationale: str
    organizational_confidence: float
    business_impact: dict[str, Any]
    consensus_breakdown: dict[str, Any]
    agent_positions: list[dict[str, Any]]
    key_risks: list[str]
    audit: dict[str, Any]
    governance_actions: list[str]


class ApprovalResponse(BaseModel):
    status: str
    case_id: str
    iteration: int | None = None
