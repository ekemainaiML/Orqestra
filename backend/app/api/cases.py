import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deliberation.adjudicator import adjudicate
from app.deliberation.agent_manager import TIER_ORDER, escalate_tier, run_independent_assessment
from app.deliberation.challenge_validator import process_challenges
from app.deliberation.scoring_engine import calculate_scores
from app.deliberation.state_machine import DeliberationStateMachine
from app.events.event_store import get_events
from app.events.publisher import publish_event
from app.governance.approval_handler import (
    approve_case,
    get_case_directives,
    modify_case,
    redeliberate_case,
    reject_case,
)
from app.governance.brief_generator import generate_brief
from app.memory.memory_service import MemoryService
from app.models.case import Case
from app.models.customer import Customer
from app.schemas.case import CaseCreate, CaseDetail, CaseResponse
from app.services.database import get_session
from app.workflows.db_loader import list_all_configs
from app.workflows.db_loader import load_workflow_config as async_load_config
from app.workflows.loader import (
    get_executive_workflow_agent,
    get_workflow_agent_ids,
)
from app.workflows.loader import (
    load_workflow_config as sync_load_config,
)

router = APIRouter(prefix="/cases", tags=["cases"])
memory_service = MemoryService()


@router.get("/workflows")
async def get_workflows(session: AsyncSession = Depends(get_session)):
    configs = await list_all_configs(session)
    return {"workflows": configs}


@router.get("", response_model=list[CaseResponse])
async def list_cases(session: AsyncSession = Depends(get_session)):
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
async def get_case(case_id: str, session: AsyncSession = Depends(get_session)):
    try:
        uid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case ID")
    case = await session.get(Case, uid)
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
async def create_case(data: CaseCreate, session: AsyncSession = Depends(get_session)):
    customer = await session.get(Customer, data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    config = await async_load_config(session, data.workflow_type)
    if config is None:
        try:
            config = sync_load_config(data.workflow_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown workflow type: {data.workflow_type}")

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
    }, session=session)

    return CaseResponse(
        id=str(case.id), customer_id=str(case.customer_id), request_text=case.request_text,
        status=case.status, iteration=case.iteration, workflow_type=case.workflow_type,
        confidence=case.confidence, completeness=case.completeness,
        created_at=case.created_at, completed_at=case.completed_at,
    )


async def _run_deliberation(case_id: str, session: AsyncSession) -> dict[str, Any]:
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    customer = await session.get(Customer, case.customer_id)
    customer_info = {"id": str(customer.id), "name": customer.name, "company": customer.company} if customer else {}

    config = await async_load_config(session, case.workflow_type)
    if config is None:
        config = sync_load_config(case.workflow_type)
    executive_agent = get_executive_workflow_agent(config)
    workflow_agent_ids = get_workflow_agent_ids(config)
    policy_defs = [p.model_dump() for p in config.policies]

    if case.status != "created":
        case.status = "created"
    sm = DeliberationStateMachine(case.status)
    sm.transition("memory_retrieval")
    case.status = sm.current_state
    await session.commit()

    memory = await memory_service.retrieve_for_case(customer_id=str(case.customer_id), session=session)
    await publish_event(case_id, "memory_retrieved", "system", {"count": len(memory)}, session=session)

    sm = DeliberationStateMachine(case.status)
    sm.transition("independent_assessment")
    case.status = sm.current_state
    await session.commit()

    directives = await get_case_directives(case_id, session)

    assessment = await run_independent_assessment(
        config=config, case_id=case_id, request_text=case.request_text, customer_info=customer_info,
        customer_id=str(case.customer_id),
        directives=directives,
        session=session,
    )

    for rec in assessment["recommendations"]:
        await publish_event(case_id, "recommendation_submitted", rec.get("agent_id", "unknown"), rec, session=session)

    sm = DeliberationStateMachine(case.status)
    sm.transition("challenge_round")
    case.status = sm.current_state
    await session.commit()

    challenge_result = await process_challenges(assessment["recommendations"], workflow_agent_ids)

    for ch in challenge_result["challenges"]:
        await publish_event(case_id, "challenge_issued", ch.get("source_agent", "unknown"), ch, session=session)

    sm = DeliberationStateMachine(case.status)
    sm.transition("consensus_scoring")
    case.status = sm.current_state
    await session.commit()

    consensus = calculate_scores(assessment["recommendations"])
    await publish_event(case_id, "consensus_calculated", "scoring_engine", consensus, session=session)

    sm = DeliberationStateMachine(case.status)
    sm.transition("adjudication")
    case.status = sm.current_state
    await session.commit()

    current_tier = config.governance.deadlock_resolution
    if current_tier == "escalate":
        current_tier = "operational"

    decision_result = await adjudicate(
        executive_agent=executive_agent,
        case_id=case_id, request_text=case.request_text, customer_info=customer_info,
        recommendations=assessment["recommendations"],
        challenges=challenge_result["challenges"],
        consensus=consensus,
        customer_id=str(case.customer_id),
        directives=directives,
        policies=policy_defs,
        model_tier_override=current_tier,
        session=session,
    )

    max_tier_idx = len(TIER_ORDER) - 1
    while decision_result["is_impasse"]:
        current_tier = escalate_tier(current_tier)
        current_tier_idx = TIER_ORDER.index(current_tier) if current_tier in TIER_ORDER else max_tier_idx
        await publish_event(case_id, "tier_escalation", "system", {
            "from_tier": TIER_ORDER[max(0, current_tier_idx - 1)],
            "to_tier": current_tier,
        }, session=session)

        assessment = await run_independent_assessment(
            config=config, case_id=case_id, request_text=case.request_text, customer_info=customer_info,
            customer_id=str(case.customer_id),
            directives=directives,
            model_tier_override=current_tier,
            session=session,
        )
        for rec in assessment["recommendations"]:
            await publish_event(case_id, "recommendation_submitted", rec.get("agent_id", "unknown"), rec, session=session)

        challenge_result = await process_challenges(assessment["recommendations"], workflow_agent_ids)
        for ch in challenge_result["challenges"]:
            await publish_event(case_id, "challenge_issued", ch.get("source_agent", "unknown"), ch, session=session)

        consensus = calculate_scores(assessment["recommendations"])
        await publish_event(case_id, "consensus_calculated", "scoring_engine", consensus, session=session)

        decision_result = await adjudicate(
            executive_agent=executive_agent,
            case_id=case_id, request_text=case.request_text, customer_info=customer_info,
            recommendations=assessment["recommendations"],
            challenges=challenge_result["challenges"],
            consensus=consensus,
            customer_id=str(case.customer_id),
            directives=directives,
            policies=policy_defs,
            model_tier_override=current_tier,
            session=session,
        )

        if current_tier_idx >= max_tier_idx:
            break

    if decision_result["is_impasse"]:
        await publish_event(case_id, "workflow_escalated", "adjudicator", decision_result, session=session)
        sm = DeliberationStateMachine(case.status)
        sm.transition("escalated")
        case.status = sm.current_state
        case.confidence = 0.0
        await session.commit()
        return {"status": "escalated", "case_id": case_id, "decision": decision_result}

    await publish_event(case_id, "decision_generated", executive_agent.role, decision_result["decision"], session=session)

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

    await publish_event(case_id, "brief_presented", "governance", brief, session=session)

    return {
        "status": "approval_pending",
        "case_id": case_id,
        "assessment": assessment,
        "challenges": challenge_result,
        "consensus": consensus,
        "decision": decision_result["decision"],
        "brief": brief,
    }


@router.post("/{case_id}/run")
async def run_deliberation(case_id: str, session: AsyncSession = Depends(get_session)):
    return await _run_deliberation(case_id, session)


@router.post("/{case_id}/approve")
async def handle_approve(case_id: str, session: AsyncSession = Depends(get_session)):
    result = await approve_case(case_id, session)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{case_id}/reject")
async def handle_reject(case_id: str, session: AsyncSession = Depends(get_session)):
    result = await reject_case(case_id, session)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{case_id}/modify")
async def handle_modify(case_id: str, directive: dict[str, Any], session: AsyncSession = Depends(get_session)):
    result = await modify_case(case_id, directive, session)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{case_id}/directives")
async def list_directives(case_id: str, session: AsyncSession = Depends(get_session)):
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return [
        {"id": str(d.id), "directive_type": d.directive_type, "value": d.value, "iteration": d.iteration}
        for d in case.directives
    ]


@router.delete("/{case_id}/directives/{directive_id}")
async def delete_directive(case_id: str, directive_id: str, session: AsyncSession = Depends(get_session)):
    from app.models.directive import Directive

    d = await session.get(Directive, uuid.UUID(directive_id))
    if not d or str(d.case_id) != case_id:
        raise HTTPException(status_code=404, detail="Directive not found")
    await session.delete(d)
    await session.commit()
    return {"message": "Directive deleted"}


@router.post("/{case_id}/redeliberate")
async def handle_redeliberate(case_id: str, session: AsyncSession = Depends(get_session)):
    result = await redeliberate_case(case_id, session)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return await _run_deliberation(case_id, session)


@router.get("/{case_id}/replay")
async def replay_case(case_id: str, session: AsyncSession = Depends(get_session)):
    try:
        uid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case ID")
    case = await session.get(Case, uid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    sm = DeliberationStateMachine(case.status)
    events_result = await get_events(case_id, session=session)

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
async def get_brief(case_id: str, session: AsyncSession = Depends(get_session)):
    try:
        uid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case ID")
    case = await session.get(Case, uid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case_id": case_id,
        "status": case.status,
        "iteration": case.iteration,
        "confidence": case.confidence,
    }
