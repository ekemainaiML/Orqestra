import uuid
from typing import Any

from app.agents.base import Challenge

REQUIRED_CHALLENGE_FIELDS = {"challenge_type", "target_agent", "statement", "evidence", "confidence"}

VALID_CHALLENGE_TYPES = {
    "factual_error", "assumption_flaw", "missing_evidence",
    "risk_underestimation", "policy_violation", "cost_miscalculation",
}


async def validate_challenge(data: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_CHALLENGE_FIELDS - set(data.keys())
    if missing:
        return {"valid": False, "reason": f"Missing fields: {missing}"}

    if data.get("challenge_type") not in VALID_CHALLENGE_TYPES:
        return {"valid": False, "reason": f"Invalid challenge type: {data.get('challenge_type')}"}

    if not isinstance(data.get("evidence"), list) or len(data["evidence"]) == 0:
        return {"valid": False, "reason": "Challenge requires at least one piece of evidence"}

    confidence = data.get("confidence", 0)
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        return {"valid": False, "reason": "Confidence must be a float between 0 and 1"}

    return {"valid": True, "reason": "ok"}


async def generate_challenge_id() -> str:
    return str(uuid.uuid4())


async def route_challenge_to_agents(
    challenge: Challenge,
    all_agent_ids: list[str],
) -> list[str]:
    return [aid for aid in all_agent_ids if aid != challenge.source_agent]


async def process_challenges(
    recommendations: list[dict[str, Any]],
    all_agent_ids: list[str],
) -> dict[str, Any]:
    challenges = []
    for rec in recommendations:
        agent_id = rec.get("agent_id")
        for other_rec in recommendations:
            other_id = other_rec.get("agent_id")
            if other_id == agent_id:
                continue

            potential = {
                "source_agent": other_id,
                "target_agent": agent_id,
                "challenge_type": "assumption_flaw",
                "statement": f"Reviewing {other_id}'s assessment of {agent_id}'s recommendation",
                "evidence": [{"source": other_id, "note": "Cross-agent review"}],
                "confidence": 0.7,
            }
            result = await validate_challenge(potential)
            if result["valid"]:
                potential["challenge_id"] = await generate_challenge_id()
                challenges.append(potential)

    return {
        "challenges": challenges,
        "total_issued": len(challenges),
    }
