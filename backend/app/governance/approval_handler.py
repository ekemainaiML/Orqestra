import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.deliberation.state_machine import DeliberationStateMachine
from app.events.publisher import publish_event
from app.models.case import Case
from app.models.directive import Directive


async def approve_case(case_id: str, session: AsyncSession) -> dict[str, Any]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        return {"error": "Case not found"}
    sm = DeliberationStateMachine(case.status)
    try:
        sm.transition("completed")
    except Exception:
        return {"error": f"Cannot approve case in status '{case.status}'"}

    case.status = "completed"
    case.completed_at = datetime.now(UTC)
    await session.commit()

    await publish_event(case_id, "decision_approved", "operator", {"case_id": case_id}, session=session)
    return {"status": "completed", "case_id": case_id}


async def reject_case(case_id: str, session: AsyncSession) -> dict[str, Any]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        return {"error": "Case not found"}
    sm = DeliberationStateMachine(case.status)
    try:
        sm.transition("rejected")
    except Exception:
        return {"error": f"Cannot reject case in status '{case.status}'"}

    case.status = "rejected"
    case.completed_at = datetime.now(UTC)
    await session.commit()

    await publish_event(case_id, "decision_rejected", "operator", {"case_id": case_id}, session=session)
    return {"status": "rejected", "case_id": case_id}


async def modify_case(case_id: str, directive: dict[str, Any], session: AsyncSession) -> dict[str, Any]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        return {"error": "Case not found"}
    sm = DeliberationStateMachine(case.status)
    try:
        sm.transition("constraint_modified")
    except Exception:
        return {"error": f"Cannot modify case in status '{case.status}'"}

    case.status = "constraint_modified"
    case.iteration += 1

    directive_record = Directive(
        case_id=case.id,
        iteration=case.iteration,
        directive_type=directive.get("type", "general"),
        value=directive,
        issued_by=directive.get("issued_by", "operator"),
    )
    session.add(directive_record)
    await session.commit()

    await publish_event(case_id, "constraint_modified", "operator", {
        "directive": directive,
        "new_iteration": case.iteration,
    }, session=session)
    return {"status": "constraint_modified", "case_id": case_id, "iteration": case.iteration}


async def redeliberate_case(case_id: str, session: AsyncSession) -> dict[str, Any]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        return {"error": "Case not found"}
    sm = DeliberationStateMachine(case.status)
    try:
        sm.transition("redeliberation_pending")
    except Exception:
        return {"error": f"Cannot redeliberate case in status '{case.status}'"}

    case.status = "redeliberation_pending"
    await session.commit()

    await publish_event(case_id, "redeliberation_started", "system", {
        "iteration": case.iteration,
    }, session=session)
    return {"status": "redeliberation_pending", "case_id": case_id, "iteration": case.iteration}


async def get_case_directives(case_id: str, session: AsyncSession) -> list[dict[str, Any]]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        return []
    return [
        {
            "id": str(d.id),
            "type": d.directive_type,
            "value": d.value,
            "iteration": d.iteration,
            "issued_by": d.issued_by,
        }
        for d in case.directives
    ]
