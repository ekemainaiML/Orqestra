from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.workflow_event import WorkflowEvent


async def get_dashboard_metrics(session: AsyncSession) -> dict[str, Any]:
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
    pending_approval = await session.execute(
        select(func.count(Case.id)).where(Case.status == "approval_pending")
    )
    created_count = await session.execute(
        select(func.count(Case.id)).where(Case.status == "created")
    )

    cases_today_val = cases_today.scalar() or 0
    total_val = total_cases.scalar() or 0
    completed_val = completed.scalar() or 0
    escalated_val = escalated.scalar() or 0
    avg_conf_val = round(float(avg_conf.scalar() or 0), 2)
    total_events_val = total_events.scalar() or 0
    memory_events_val = memory_events.scalar() or 0
    pending_approval_val = pending_approval.scalar() or 0
    created_val = created_count.scalar() or 0

    non_created = total_val - created_val
    resolved = completed_val + escalated_val
    approval_rate = round(resolved / non_created, 4) if non_created > 0 else 0.0
    escalation_rate = round(escalated_val / resolved, 4) if resolved > 0 else 0.0
    memory_utilization_rate = round(memory_events_val / total_events_val, 4) if total_events_val > 0 else 0.0

    completed_cases_list = await session.execute(
        select(Case).where(Case.status.in_(["completed", "closed"])).where(Case.completed_at.isnot(None))
    )
    avg_deliberation_time_s = 0.0
    delib_times: list[float] = []
    for c in completed_cases_list.scalars():
        if c.created_at and c.completed_at:
            delta = (c.completed_at - c.created_at).total_seconds()
            if delta > 0:
                delib_times.append(delta)
    if delib_times:
        avg_deliberation_time_s = round(sum(delib_times) / len(delib_times), 1)

    all_recs = await session.execute(
        select(WorkflowEvent.actor, WorkflowEvent.payload).where(
            WorkflowEvent.event_type == "recommendation_submitted"
        )
    )
    dept_scores: dict[str, list[float]] = {}
    for row in all_recs:
        actor = row[0]
        payload = row[1] or {}
        conf = payload.get("confidence")
        if conf is not None:
            dept_scores.setdefault(actor, []).append(float(conf))
    dept_perf: dict[str, float] = {}
    for actor, scores in dept_scores.items():
        if scores:
            dept_perf[actor] = round(sum(scores) / len(scores), 4)

    return {
        "cases_today": cases_today_val,
        "total_cases": total_val,
        "completed_cases": completed_val,
        "escalated_cases": escalated_val,
        "average_confidence": avg_conf_val,
        "total_events": total_events_val,
        "memory_retrievals": memory_events_val,
        "approval_rate": approval_rate,
        "escalation_rate": escalation_rate,
        "memory_utilization_rate": memory_utilization_rate,
        "avg_deliberation_time_s": avg_deliberation_time_s,
        "department_performance": dept_perf,
        "pending_approval": pending_approval_val,
    }


async def get_case_aggregates(case_id: str, session: AsyncSession) -> dict[str, Any]:
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
