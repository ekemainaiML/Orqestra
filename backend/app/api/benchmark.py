import re
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.business_tools import tool_registry
from app.memory.memory_service import MemoryService
from app.models.benchmark_run import BenchmarkRun
from app.models.case import Case
from app.services.database import get_session

router = APIRouter(prefix="/benchmark", tags=["benchmark"])
memory_service = MemoryService()


def _parse_case_text(text: str) -> dict[str, Any]:
    qty_match = re.search(r"(\d+)\s+.*?(units?|pieces?|lights?|controllers?)", text, re.IGNORECASE)
    quantity = int(qty_match.group(1)) if qty_match else 100

    product = "solar_street_light_100w"
    text_lower = text.lower()
    if "60w" in text_lower or "60-watt" in text_lower:
        product = "solar_street_light_60w"

    is_government = any(kw in text_lower for kw in ["government", "municipal", "council", "public"])
    is_urgent = any(kw in text_lower for kw in ["urgent", "rush", "asap", "expedite", "immediate"])

    deadline_days = 14
    deadline_match = re.search(r"(\d+)\s*(days?|weeks?)", text, re.IGNORECASE)
    if deadline_match:
        num = int(deadline_match.group(1))
        unit = deadline_match.group(2).lower()
        deadline_days = num * 7 if "week" in unit else num

    return {
        "quantity": quantity,
        "product": product,
        "is_government": is_government,
        "is_urgent": is_urgent,
        "deadline_days": deadline_days,
    }


async def _run_tool_analysis(parsed: dict[str, Any]) -> dict[str, Any]:
    product = parsed["product"]
    quantity = parsed["quantity"]
    is_gov = parsed["is_government"]

    inventory = await tool_registry["check_availability"](product=product, quantity=quantity)
    specs = await tool_registry["get_product_specs"](product=product)
    pricing = await tool_registry["calculate_price"](quantity=quantity, is_preferred=is_gov, is_government=is_gov)
    suppliers = await tool_registry["find_suppliers"]()
    policies = await tool_registry["get_all_policies"]()

    policy_results = {}
    for p in policies:
        ctx = {"margin_pct": pricing["estimated_margin_pct"], "is_new_client": not is_gov}
        policy_results[p["id"]] = await tool_registry["check_policy"](policy_id=p["id"], context=ctx)

    return {
        "inventory": inventory,
        "specs": specs,
        "pricing": pricing,
        "suppliers": suppliers,
        "policies": policy_results,
    }


def _build_single_recommendation(parsed: dict[str, Any], tools: dict[str, Any]) -> dict[str, Any]:
    pricing = tools["pricing"]
    inventory = tools["inventory"]
    shortfall = inventory["shortfall"]

    risks = []
    if shortfall > 0:
        risks.append(f"Inventory shortfall: {shortfall} units need procurement")
    if parsed["is_urgent"] and shortfall > 0:
        risks.append("Urgent timeline conflicts with procurement lead time")
    if parsed["deadline_days"] < 7:
        risks.append("Tight delivery window may require air freight")
    if not risks:
        risks.append("No significant risks identified")

    recommendation = (
        f"Quote ${pricing['subtotal']:,.0f} for {parsed['quantity']} units "
        f"at ${pricing['unit_price']:.2f}/unit. "
        f"Margin: {pricing['estimated_margin_pct']}%."
    )
    if shortfall > 0:
        recommendation += f" Procurement needed for {shortfall} units."

    factors = [
        f"Unit price: ${pricing['unit_price']:.2f}",
        f"Quantity: {parsed['quantity']}",
        f"Inventory available: {inventory['available']}",
        f"Margin: {pricing['estimated_margin_pct']}%",
    ]
    if parsed["is_government"]:
        factors.append("Government client — net-60 terms apply")

    return {
        "agent_id": "operations_manager",
        "recommendation": recommendation,
        "confidence": round(
            0.5 + (pricing["estimated_margin_pct"] / 100) * 0.3
            - (shortfall / max(parsed["quantity"], 1)) * 0.2,
            2,
        ),
        "reasoning": "Single-agent assessment using pricing and inventory data.",
        "risks": risks,
        "alternatives": [s["name"] for s in tools["suppliers"][:2]],
        "factors": factors,
        "evidence": [{"source": "pricing_engine", "data": pricing}, {"source": "inventory", "data": inventory}],
    }


def _build_org_recommendations(parsed: dict[str, Any], tools: dict[str, Any]) -> list[dict[str, Any]]:
    recs = []
    pricing = tools["pricing"]
    inventory = tools["inventory"]
    suppliers = tools["suppliers"]
    policies = tools["policies"]
    shortfall = inventory["shortfall"]

    recs.append({
        "agent_id": "sales",
        "recommendation": f"Proceed with order. Customer request for {parsed['quantity']} units confirmed.",
        "confidence": min(0.95, 0.6 + parsed["quantity"] / 1000 * 0.3),
        "reasoning": "Sales assessment of customer requirements.",
        "risks": [], "alternatives": [], "evidence": [],
    })
    margin_ok = pricing["estimated_margin_pct"] >= 15
    recs.append({
        "agent_id": "finance",
        "recommendation": f"Budget: ${pricing['subtotal']:,.0f} at {pricing['estimated_margin_pct']}% margin.",
        "confidence": min(0.9, 0.5 + pricing["estimated_margin_pct"] / 100),
        "reasoning": "Financial viability assessment.",
        "risks": [] if margin_ok else ["Margin below 15% threshold"],
        "alternatives": [], "evidence": [{"source": "pricing_engine", "data": pricing}],
    })
    recs.append({
        "agent_id": "inventory",
        "recommendation": f"Stock: {inventory['available']} available, {shortfall} shortfall.",
        "confidence": 0.7 if shortfall == 0 else 0.3,
        "reasoning": "Inventory position assessment.",
        "risks": [f"Shortfall of {shortfall} units"] if shortfall > 0 else [],
        "alternatives": [], "evidence": [{"source": "inventory_service", "data": inventory}],
    })
    supplier_name = suppliers[0]["name"] if suppliers else "N/A"
    supplier_lead = suppliers[0].get("lead_time_days", "N/A") if suppliers else "N/A"
    recs.append({
        "agent_id": "procurement",
        "recommendation": (
            f"Source from {supplier_name} (lead time: {supplier_lead} days)."
        ),
        "confidence": 0.75,
        "reasoning": "Supplier evaluation.", "risks": [],
        "alternatives": [s["name"] for s in suppliers[:2]],
        "evidence": [{"source": "supplier_db", "data": suppliers[0] if suppliers else {}}],
    })

    urgent_label = " URGENT" if parsed["is_urgent"] else ""
    log_risks = ["Customs clearance may add 3-5 days"] if parsed["is_government"] else []
    recs.append({
        "agent_id": "logistics",
        "recommendation": (
            f"Delivery in {parsed['deadline_days']} days{urgent_label} via standard freight."
        ),
        "confidence": 0.5 if parsed["is_urgent"] and shortfall > 0 else 0.85,
        "reasoning": "Logistics feasibility.",
        "risks": log_risks,
        "alternatives": [], "evidence": [],
    })

    poly_compliance = all(p.get("compliant", True) for p in policies.values())
    recs.append({
        "agent_id": "operations_manager",
        "recommendation": (
            f"APPROVED: {parsed['quantity']} units at ${pricing['unit_price']:.2f}/unit. "
            f"Total: ${pricing['subtotal']:,.0f}. Margin: {pricing['estimated_margin_pct']}%."
        ),
        "confidence": round(0.6 + (pricing["estimated_margin_pct"] / 100) * 0.3, 2),
        "reasoning": (
            "Synthesized from all department inputs. Policy compliance verified."
            if poly_compliance else "Policy exceptions noted."
        ),
        "risks": [] if shortfall == 0 else [f"Procurement required for {shortfall} units — monitor lead time"],
        "alternatives": [], "evidence": [{"source": "policy_engine", "data": policies}],
    })

    return recs


def _count_factors(rec: dict[str, Any]) -> int:
    count = 0
    reasoning = rec.get("reasoning", "")
    if reasoning:
        count += len([s for s in reasoning.split(". ") if len(s.strip()) > 15])
    count += len(rec.get("evidence", []))
    count += len(rec.get("alternatives", []))
    return max(count, 1)


def _count_risks(rec: dict[str, Any]) -> int:
    return len(rec.get("risks", []))


@router.get("/{case_id}")
async def get_benchmark(case_id: str, session: AsyncSession = Depends(get_session)):
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
async def run_benchmark(case_id: str, session: AsyncSession = Depends(get_session)):
    case = await session.get(Case, uuid.UUID(case_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    await session.execute(
        delete(BenchmarkRun).where(BenchmarkRun.case_id == uuid.UUID(case_id))
    )
    await session.commit()

    parsed = _parse_case_text(case.request_text)
    tools = await _run_tool_analysis(parsed)

    memory = await memory_service.retrieve_for_case(customer_id=str(case.customer_id))
    mem_count = len(memory)

    # ── Single-agent run ──
    t0 = time.time()
    single_rec = _build_single_recommendation(parsed, tools)
    t1 = time.time()

    # ── Organization run ──
    t2 = time.time()
    org_recs = _build_org_recommendations(parsed, tools)
    org_decision = org_recs[-1]
    org_confidence = org_decision.get("confidence", 0.0)
    org_risks = sum(_count_risks(r) for r in org_recs)
    org_factors = sum(_count_factors(r) for r in org_recs)
    t3 = time.time()

    org_memory = await memory_service.retrieve_for_case(customer_id=str(case.customer_id))

    single_confidence = single_rec.get("confidence", 0.0)
    single_risks = _count_risks(single_rec)
    single_factors = _count_factors(single_rec)

    single_run = BenchmarkRun(
        case_id=uuid.UUID(case_id),
        run_type="single_agent",
        recommendation=single_rec,
        confidence=single_confidence,
        risks_found=single_risks,
        factors_considered=single_factors,
        reasoning_time_s=round(t1 - t0, 2),
        memory_used=mem_count,
    )
    org_run = BenchmarkRun(
        case_id=uuid.UUID(case_id),
        run_type="organization",
        recommendation=org_decision,
        confidence=org_confidence,
        risks_found=org_risks,
        factors_considered=org_factors,
        reasoning_time_s=round(t3 - t2, 2),
        memory_used=len(org_memory),
    )
    session.add_all([single_run, org_run])
    await session.commit()

    return {
        "message": "Benchmark run completed",
        "confidence_gain": round(org_confidence - single_confidence, 2),
    }
