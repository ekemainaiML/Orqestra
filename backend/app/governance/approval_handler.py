import uuid
from datetime import datetime, timezone
from typing import Any

from app.deliberation.state_machine import DeliberationStateMachine
from app.events.publisher import publish_event
from app.models.case import Case
from app.services.database import async_session


async def approve_case(case_id: str) -> dict[str, Any]:
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            return {"error": "Case not found"}
        sm = DeliberationStateMachine(case.status)
        try:
            sm.transition("completed")
        except Exception:
            return {"error": f"Cannot approve case in status '{case.status}'"}

        case.status = "completed"
        case.completed_at = datetime.now(timezone.utc)
        await session.commit()

    await publish_event(case_id, "decision_approved", "operator", {"case_id": case_id})
    return {"status": "completed", "case_id": case_id}


async def reject_case(case_id: str) -> dict[str, Any]:
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            return {"error": "Case not found"}
        sm = DeliberationStateMachine(case.status)
        try:
            sm.transition("rejected")
        except Exception:
            return {"error": f"Cannot reject case in status '{case.status}'"}

        case.status = "rejected"
        case.completed_at = datetime.now(timezone.utc)
        await session.commit()

    await publish_event(case_id, "decision_rejected", "operator", {"case_id": case_id})
    return {"status": "rejected", "case_id": case_id}


async def modify_case(case_id: str, directive: dict[str, Any]) -> dict[str, Any]:
    async with async_session() as session:
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
        await session.commit()

    await publish_event(case_id, "constraint_modified", "operator", {
        "directive": directive,
        "new_iteration": case.iteration,
    })
    return {"status": "constraint_modified", "case_id": case_id, "iteration": case.iteration}
