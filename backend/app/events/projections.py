from typing import Any

from sqlalchemy import func, select, and_

from app.models.case import Case
from app.models.workflow_event import WorkflowEvent
from app.services.database import async_session


async def get_dashboard_metrics() -> dict[str, Any]:
    async with async_session() as session:
        today = func.date_trunc("day", func.now())

        cases_today = await session.execute(
            select(func.count(Case.id)).where(func.date_trunc("day", Case.created_at) == today)
        )
        total_cases = await session.execute(select(func.count(Case.id)))
        completed = await session.execute(
            select(func.count(Case.id)).where(Case.status.in_(["completed", "closed"]))
        )
        escalated = await session.execute(
            select(func.count(Case.id)).where(Case.status == "escalated")
        )

        avg_conf = await session.execute(select(func.avg(Case.confidence)).where(Case.confidence.isnot(None)))

        total_events = await session.execute(select(func.count(WorkflowEvent.id)))
        memory_events = await session.execute(
            select(func.count(WorkflowEvent.id)).where(WorkflowEvent.event_type == "memory_retrieved")
        )

        return {
            "cases_today": cases_today.scalar() or 0,
            "total_cases": total_cases.scalar() or 0,
            "completed_cases": completed.scalar() or 0,
            "escalated_cases": escalated.scalar() or 0,
            "average_confidence": round(float(avg_conf.scalar() or 0), 2),
            "total_events": total_events.scalar() or 0,
            "memory_retrievals": memory_events.scalar() or 0,
        }


async def get_case_aggregates(case_id: str) -> dict[str, Any]:
    async with async_session() as session:
        events = await session.execute(
            select(WorkflowEvent).where(WorkflowEvent.case_id == case_id).order_by(WorkflowEvent.timestamp)
        )
        event_list = events.scalars().all()

        return {
            "total_events": len(event_list),
            "event_types": list(set(e.event_type for e in event_list)),
            "duration_s": (
                (event_list[-1].timestamp - event_list[0].timestamp).total_seconds()
                if len(event_list) >= 2 else 0
            ),
        }
