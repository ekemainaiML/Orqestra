import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.agents.registry import get_all_agent_ids
from app.deliberation.adjudicator import adjudicate
from app.deliberation.agent_manager import run_independent_assessment
from app.deliberation.challenge_validator import process_challenges
from app.deliberation.scoring_engine import calculate_scores
from app.deliberation.state_machine import DeliberationStateMachine
from app.events.event_store import get_events
from app.events.publisher import publish_event
from app.governance.approval_handler import approve_case, modify_case, reject_case
from app.governance.brief_generator import generate_brief
from app.memory.memory_service import MemoryService
from app.models.case import Case
from app.models.customer import Customer
from app.schemas.case import CaseCreate, CaseDetail, CaseResponse
from app.services.database import async_session

router = APIRouter(prefix="/cases", tags=["cases"])
memory_service = MemoryService()


@router.get("", response_model=list[CaseResponse])
async def list_cases():
    async with async_session() as session:
        result = await session.execute(select(Case).order_by(Case.created_at.desc()))
        cases = result.scalars().all()
        return [
            CaseResponse(
                id=str(c.id), customer_id=str(c.customer_id), request_text=c.request_text,
                status=c.status, iteration=c.iteration, workflow_type=c.workflow_type,
                confidence=c.confidence, completeness=c.completeness,
                created_at=c.created_at, completed_at=c.completed_at,
            )
            for c in cases
        ]


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return CaseDetail(
            id=str(case.id), customer_id=str(case.customer_id), request_text=case.request_text,
            status=case.status, iteration=case.iteration, workflow_type=case.workflow_type,
            confidence=case.confidence, completeness=case.completeness,
            created_at=case.created_at, completed_at=case.completed_at,
            events=[
                {"id": str(e.id), "event_type": e.event_type, "actor": e.actor, "payload": e.payload,
                 "iteration": e.iteration, "timestamp": e.timestamp.isoformat() if e.timestamp else None}
                for e in case.events
            ],
            directives=[
                {"id": str(d.id), "directive_type": d.directive_type, "value": d.value, "iteration": d.iteration}
                for d in case.directives
            ],
        )


@router.post("", response_model=CaseResponse)
async def create_case(data: CaseCreate):
    async with async_session() as session:
        customer = await session.get(Customer, data.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        case = Case(
            customer_id=data.customer_id,
            request_text=data.request_text,
            workflow_type=data.workflow_type,
        )
        session.add(case)
        await session.commit()
        await session.refresh(case)

        await publish_event(str(case.id), "case_created", "system", {
            "customer_id": str(data.customer_id),
            "workflow_type": data.workflow_type,
        })

        return CaseResponse(
            id=str(case.id), customer_id=str(case.customer_id), request_text=case.request_text,
            status=case.status, iteration=case.iteration, workflow_type=case.workflow_type,
            confidence=case.confidence, completeness=case.completeness,
            created_at=case.created_at, completed_at=case.completed_at,
        )


@router.post("/{case_id}/run")
async def run_deliberation(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        customer = await session.get(Customer, case.customer_id)
        customer_info = {"id": str(customer.id), "name": customer.name, "company": customer.company} if customer else {}

        sm = DeliberationStateMachine(case.status)

        sm.transition("memory_retrieval")
        case.status = sm.current_state
        await session.commit()

    memory = await memory_service.retrieve_for_case(customer_id=str(case.customer_id))

    await publish_event(case_id, "memory_retrieved", "system", {"count": len(memory)})

    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        assert case is not None, "Case was deleted mid-deliberation"
        sm = DeliberationStateMachine(case.status)
        sm.transition("independent_assessment")
        case.status = sm.current_state
        await session.commit()

    assessment = await run_independent_assessment(
        case_id=case_id, request_text=case.request_text, customer_info=customer_info,
        customer_id=str(case.customer_id),
    )

    for rec in assessment["recommendations"]:
        await publish_event(case_id, "recommendation_submitted", rec.get("agent_id", "unknown"), rec)

    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        assert case is not None
        sm = DeliberationStateMachine(case.status)
        sm.transition("challenge_round")
        case.status = sm.current_state
        await session.commit()

    all_agent_ids = get_all_agent_ids()
    challenge_result = await process_challenges(assessment["recommendations"], all_agent_ids)

    for ch in challenge_result["challenges"]:
        await publish_event(case_id, "challenge_issued", ch.get("source_agent", "unknown"), ch)

    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        assert case is not None
        sm = DeliberationStateMachine(case.status)
        sm.transition("consensus_scoring")
        case.status = sm.current_state
        await session.commit()

    consensus = calculate_scores(assessment["recommendations"])
    await publish_event(case_id, "consensus_calculated", "scoring_engine", consensus)

    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        assert case is not None
        sm = DeliberationStateMachine(case.status)
        sm.transition("adjudication")
        case.status = sm.current_state
        await session.commit()

    decision_result = await adjudicate(
        case_id=case_id, request_text=case.request_text, customer_info=customer_info,
        recommendations=assessment["recommendations"],
        challenges=challenge_result["challenges"],
        consensus=consensus,
        customer_id=str(case.customer_id),
    )

    if decision_result["is_impasse"]:
        await publish_event(case_id, "workflow_escalated", "adjudicator", decision_result)
        async with async_session() as session:
            case = await session.get(Case, uuid.UUID(case_id))
            assert case is not None
            sm = DeliberationStateMachine(case.status)
            sm.transition("escalated")
            case.status = sm.current_state
            case.confidence = 0.0
            await session.commit()
        return {"status": "escalated", "case_id": case_id, "decision": decision_result}

    await publish_event(case_id, "decision_generated", "operations_manager", decision_result["decision"])

    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        assert case is not None
        sm = DeliberationStateMachine(case.status)
        sm.transition("approval_pending")
        case.status = sm.current_state
        case.confidence = decision_result["decision"].get("confidence")
        await session.commit()

    brief = await generate_brief(
        case={"id": case_id, "request_text": case.request_text, "status": "approval_pending"},
        customer=customer_info,
        decision=decision_result["decision"],
        recommendations=assessment["recommendations"],
        challenges=challenge_result["challenges"],
        consensus=consensus,
        iteration=case.iteration,
    )

    await publish_event(case_id, "brief_presented", "governance", brief)

    return {
        "status": "approval_pending",
        "case_id": case_id,
        "assessment": assessment,
        "challenges": challenge_result,
        "consensus": consensus,
        "decision": decision_result["decision"],
        "brief": brief,
    }


@router.post("/{case_id}/approve")
async def handle_approve(case_id: str):
    result = await approve_case(case_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{case_id}/reject")
async def handle_reject(case_id: str):
    result = await reject_case(case_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{case_id}/modify")
async def handle_modify(case_id: str, directive: dict[str, Any]):
    result = await modify_case(case_id, directive)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{case_id}/replay")
async def replay_case(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        sm = DeliberationStateMachine(case.status)
        events_result = await get_events(case_id)

        return {
            "case_id": case_id,
            "status": case.status,
            "iteration": case.iteration,
            "state_machine": sm.to_dict(),
            "states": ["created", "memory_retrieval", "independent_assessment",
                       "challenge_round", "consensus_scoring", "adjudication",
                       "approval_pending", "completed", "escalated"],
            "events": events_result,
        }


@router.get("/{case_id}/brief")
async def get_brief(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return {
            "case_id": case_id,
            "status": case.status,
            "iteration": case.iteration,
            "confidence": case.confidence,
        }
