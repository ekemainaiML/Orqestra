import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_event import WorkflowEvent


async def append_event(
    case_id: str,
    event_type: str,
    actor: str,
    payload: dict[str, Any] | None = None,
    iteration: int = 0,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    async def _do(s: AsyncSession) -> dict[str, Any]:
        event = WorkflowEvent(
            case_id=uuid.UUID(case_id),
            event_type=event_type,
            actor=actor,
            payload=payload,
            iteration=iteration,
        )
        s.add(event)
        await s.commit()
        await s.refresh(event)
        return {
            "id": str(event.id),
            "case_id": str(event.case_id),
            "event_type": event.event_type,
            "actor": event.actor,
            "payload": event.payload,
            "iteration": event.iteration,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def get_events(
    case_id: str,
    event_type: str | None = None,
    iteration: int | None = None,
    limit: int = 100,
    session: AsyncSession | None = None,
) -> list[dict[str, Any]]:
    async def _do(s: AsyncSession) -> list[dict[str, Any]]:
        stmt = select(WorkflowEvent).where(WorkflowEvent.case_id == uuid.UUID(case_id))
        if event_type:
            stmt = stmt.where(WorkflowEvent.event_type == event_type)
        if iteration is not None:
            stmt = stmt.where(WorkflowEvent.iteration == iteration)
        stmt = stmt.order_by(WorkflowEvent.timestamp.asc()).limit(limit)
        result = await s.execute(stmt)
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

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def get_event_count(case_id: str, session: AsyncSession | None = None) -> int:
    async def _do(s: AsyncSession) -> int:
        stmt = select(WorkflowEvent).where(WorkflowEvent.case_id == uuid.UUID(case_id))
        result = await s.execute(stmt)
        return len(result.scalars().all())

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)
