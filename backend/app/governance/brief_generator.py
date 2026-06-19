from typing import Any


async def generate_brief(
    case: dict[str, Any],
    customer: dict[str, Any],
    decision: dict[str, Any] | None,
    recommendations: list[dict[str, Any]],
    challenges: list[dict[str, Any]],
    consensus: dict[str, Any],
    iteration: int,
) -> dict[str, Any]:
    agent_positions = []
    for rec in recommendations:
        agent_positions.append({
            "agent_id": rec.get("agent_id"),
            "recommendation": rec.get("recommendation", ""),
            "confidence": rec.get("confidence"),
            "status": "supporting" if rec.get("confidence", 0) >= 0.7 else "concerned",
        })

    consensus_breakdown = consensus.get("dimension_scores", {})
    overall = consensus.get("overall_consensus", 0)

    risk_level = _classify_risk(overall, len(challenges))
    risks = []
    for rec in recommendations:
        risks.extend(rec.get("risks", []))

    return {
        "case_id": case.get("id"),
        "customer_name": customer.get("name", "Unknown"),
        "request_summary": case.get("request_text", "")[:200],
        "status": case.get("status"),
        "iteration": iteration,
        "recommended_strategy": decision.get("recommendation") if decision else "Pending",
        "rationale": decision.get("reasoning") if decision else "Awaiting adjudication",
        "organizational_confidence": decision.get("confidence") if decision else 0,
        "business_impact": {
            "consensus_score": overall,
            "risk_classification": risk_level,
            "challenges_raised": len(challenges),
        },
        "consensus_breakdown": {
            "overall": overall,
            "dimensions": consensus_breakdown,
        },
        "agent_positions": agent_positions,
        "key_risks": list(set(risks))[:5],
        "memory_evidence": {
            "total_retrieved": 0,
            "sources": [],
        },
        "audit": {
            "trace_available": True,
            "total_decisions": len(recommendations),
            "challenges_issued": len(challenges),
        },
        "governance_actions": ["approve", "reject", "modify"],
    }


def _classify_risk(consensus_score: float, challenge_count: int) -> str:
    if consensus_score >= 0.85 and challenge_count <= 1:
        return "low"
    elif consensus_score >= 0.65 and challenge_count <= 3:
        return "medium"
    return "high"
