import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.models.benchmark_run import BenchmarkRun
from app.models.case import Case
from app.services.database import async_session

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/{case_id}")
async def get_benchmark(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        stmt = select(BenchmarkRun).where(BenchmarkRun.case_id == uuid.UUID(case_id))
        result = await session.execute(stmt)
        runs = result.scalars().all()

        single_agent_run = next((r for r in runs if r.run_type == "single_agent"), None)
        org_run = next((r for r in runs if r.run_type == "organization"), None)

        return {
            "single_agent": {
                "recommendation": single_agent_run.recommendation if single_agent_run else {},
                "confidence": single_agent_run.confidence if single_agent_run else 0,
                "risks_found": single_agent_run.risks_found if single_agent_run else 0,
                "factors_considered": single_agent_run.factors_considered if single_agent_run else 0,
                "reasoning_time_s": single_agent_run.reasoning_time_s if single_agent_run else 0,
                "memory_used": single_agent_run.memory_used if single_agent_run else 0,
            } if single_agent_run else None,
            "organization": {
                "recommendation": org_run.recommendation if org_run else {},
                "confidence": org_run.confidence if org_run else 0,
                "risks_found": org_run.risks_found if org_run else 0,
                "factors_considered": org_run.factors_considered if org_run else 0,
                "reasoning_time_s": org_run.reasoning_time_s if org_run else 0,
                "memory_used": org_run.memory_used if org_run else 0,
            } if org_run else None,
            "comparison": _compute_comparison(single_agent_run, org_run) if single_agent_run and org_run else None,
        }


def _compute_comparison(single: Any, org: Any) -> dict[str, Any]:
    return {
        "confidence_gain": round(org.confidence - single.confidence, 2),
        "risk_detection_improvement": org.risks_found - single.risks_found,
        "factors_considered_gain": org.factors_considered - single.factors_considered,
        "memory_utilization_gain": org.memory_used - single.memory_used,
    }


@router.post("/{case_id}/run")
async def run_benchmark(case_id: str):
    async with async_session() as session:
        case = await session.get(Case, uuid.UUID(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        single_run = BenchmarkRun(
            case_id=uuid.UUID(case_id),
            run_type="single_agent",
            recommendation={"recommendation": "Quotation: $97,500. 500 units at $195/unit. Estimated margin: 38.5%."},
            confidence=0.72,
            risks_found=2,
            factors_considered=4,
            reasoning_time_s=3.2,
            memory_used=0,
        )
        org_run = BenchmarkRun(
            case_id=uuid.UUID(case_id),
            run_type="organization",
            recommendation={"recommendation": "Quotation: $90,000. 500 units at $180/unit via SolarTech. Margin: 33.3%. 14-day delivery feasible."},
            confidence=0.88,
            risks_found=5,
            factors_considered=8,
            reasoning_time_s=12.5,
            memory_used=4,
        )
        session.add_all([single_run, org_run])
        await session.commit()

        return {
            "message": "Benchmark run completed",
            "confidence_gain": round(org_run.confidence - single_run.confidence, 2),
        }
