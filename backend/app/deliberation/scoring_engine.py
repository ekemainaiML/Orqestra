from typing import Any

SCORE_DIMENSIONS = [
    "customer_satisfaction",
    "profitability",
    "operational_risk",
    "delivery_reliability",
    "policy_compliance",
]

AGENT_EXPERTISE: dict[str, list[str]] = {
    "sales": ["customer_satisfaction"],
    "finance": ["profitability", "policy_compliance"],
    "inventory": ["operational_risk", "delivery_reliability"],
    "procurement": ["profitability", "operational_risk"],
    "logistics": ["delivery_reliability", "operational_risk"],
}


def calculate_scores(recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    dimension_scores: dict[str, list[float]] = {d: [] for d in SCORE_DIMENSIONS}
    agent_scores: dict[str, dict[str, float]] = {}

    for rec in recommendations:
        agent_id = rec.get("agent_id", "unknown")
        confidence = rec.get("confidence", 0.5)
        agent_scores[agent_id] = {}

        for dim in AGENT_EXPERTISE.get(agent_id, []):
            score = confidence * _score_from_recommendation(rec, dim)
            dimension_scores[dim].append(score)
            agent_scores[agent_id][dim] = round(score, 2)

    consensus: dict[str, Any] = {}
    for dim, scores in dimension_scores.items():
        if scores:
            consensus[dim] = round(sum(scores) / len(scores), 2)
        else:
            consensus[dim] = 0.0

    overall = round(sum(consensus.values()) / len(consensus), 2)

    return {
        "overall_consensus": overall,
        "dimension_scores": consensus,
        "agent_scores": agent_scores,
        "score_breakdown": {
            "dimensions_evaluated": [d for d in SCORE_DIMENSIONS if dimension_scores[d]],
            "agents_contributing": list(agent_scores.keys()),
        },
    }


def _score_from_recommendation(rec: dict[str, Any], dimension: str) -> float:
    mapping = {
        "customer_satisfaction": 0.85,
        "profitability": 0.80,
        "operational_risk": 0.75,
        "delivery_reliability": 0.80,
        "policy_compliance": 0.90,
    }
    return mapping.get(dimension, 0.75)
