from typing import Any

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: str
    case_id: str
    event_type: str
    actor: str
    payload: dict[str, Any] | None = None
    iteration: int
    timestamp: str | None = None
