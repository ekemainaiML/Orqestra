import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, and_

from app.models.workflow_event import WorkflowEvent
from app.services.database import async_session


async def append_event(
    case_id: str,
    event_type: str,
    actor: str,
    payload: dict[str, Any] | None = None,
    iteration: int = 0,
) -> dict[str, Any]:
    async with async_session() as session:
        event = WorkflowEvent(
            case_id=uuid.UUID(case_id),
            event_type=event_type,
            actor=actor,
            payload=payload,
            iteration=iteration,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return {
            "id": str(event.id),
            "case_id": str(event.case_id),
            "event_type": event.event_type,
            "actor": event.actor,
            "payload": event.payload,
            "iteration": event.iteration,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }


async def get_events(
    case_id: str,
    event_type: str | None = None,
    iteration: int | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    async with async_session() as session:
        stmt = select(WorkflowEvent).where(WorkflowEvent.case_id == uuid.UUID(case_id))
        if event_type:
            stmt = stmt.where(WorkflowEvent.event_type == event_type)
        if iteration is not None:
            stmt = stmt.where(WorkflowEvent.iteration == iteration)
        stmt = stmt.order_by(WorkflowEvent.timestamp.asc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": str(e.id),
                "case_id": str(e.case_id),
                "event_type": e.event_type,
                "actor": e.actor,
                "payload": e.payload,
                "iteration": e.iteration,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
            for e in result.scalars().all()
        ]


async def get_event_count(case_id: str) -> int:
    async with async_session() as session:
        stmt = select(WorkflowEvent).where(WorkflowEvent.case_id == uuid.UUID(case_id))
        result = await session.execute(stmt)
        return len(result.scalars().all())
