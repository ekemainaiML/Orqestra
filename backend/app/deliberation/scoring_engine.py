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

DIMENSION_KEYWORDS: dict[str, list[str]] = {
    "customer_satisfaction": [
        "customer", "client", "satisfaction", "deadline", "quality",
        "relationship", "service", "support", "complaint", "feedback",
    ],
    "profitability": [
        "profit", "margin", "revenue", "cost", "pricing", "discount",
        "budget", "financial", "savings", "overhead", "roi",
    ],
    "operational_risk": [
        "risk", "shortage", "delay", "failure", "bottleneck",
        "capacity", "constraint", "buffer", "safety", "stockout",
    ],
    "delivery_reliability": [
        "delivery", "lead time", "shipping", "logistics", "on-time",
        "transport", "schedule", "timeline", "expedite", "carrier",
    ],
    "policy_compliance": [
        "policy", "compliance", "regulation", "approval", "audit",
        "standard", "procedure", "rule", "requirement", "governance",
    ],
}


def _score_from_recommendation(rec: dict[str, Any], dimension: str) -> float:
    text = _get_recommendation_text(rec).lower()
    keywords = DIMENSION_KEYWORDS.get(dimension, [])

    if not text:
        return 0.5

    matches = sum(1 for kw in keywords if kw.lower() in text)
    total = len(keywords)

    if total == 0:
        return 0.5

    raw_score = matches / total
    confidence = rec.get("confidence", 0.5)

    return round(0.3 + raw_score * 0.5 + confidence * 0.2, 2)


def _get_recommendation_text(rec: dict[str, Any]) -> str:
    parts = [
        rec.get("recommendation", ""),
        rec.get("reasoning", ""),
        " ".join(rec.get("risks", [])),
        " ".join(rec.get("alternatives", [])),
    ]
    return " ".join(p for p in parts if p)


def _estimate_risk_count(recommendations: list[dict[str, Any]]) -> list[str]:
    all_risks: list[str] = []
    for rec in recommendations:
        all_risks.extend(rec.get("risks", []))
    seen = set()
    unique = []
    for r in all_risks:
        key = r.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def calculate_scores(recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    dimension_scores: dict[str, list[float]] = {d: [] for d in SCORE_DIMENSIONS}
    agent_scores: dict[str, dict[str, float]] = {}

    for rec in recommendations:
        agent_id = rec.get("agent_id", "unknown")
        agent_scores[agent_id] = {}

        for dim in AGENT_EXPERTISE.get(agent_id, []):
            score = _score_from_recommendation(rec, dim)
            dimension_scores[dim].append(score)
            agent_scores[agent_id][dim] = round(score, 2)

    consensus: dict[str, float] = {}
    for dim, scores in dimension_scores.items():
        if scores:
            consensus[dim] = round(sum(scores) / len(scores), 2)
        else:
            consensus[dim] = 0.0

    overall = round(sum(consensus.values()) / len(consensus), 2)

    identified_risks = _estimate_risk_count(recommendations)

    return {
        "overall_consensus": overall,
        "dimension_scores": consensus,
        "agent_scores": agent_scores,
        "risks": identified_risks,
        "score_breakdown": {
            "dimensions_evaluated": [d for d in SCORE_DIMENSIONS if dimension_scores[d]],
            "agents_contributing": list(agent_scores.keys()),
        },
    }
