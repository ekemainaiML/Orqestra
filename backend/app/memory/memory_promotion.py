from typing import Any

PROMOTION_RULES: dict[str, list[str]] = {
    "major_customer_decisions": ["customer", "decision"],
    "successful_negotiations": ["customer", "supplier"],
    "supplier_failures": ["supplier"],
    "policy_exceptions": ["policy"],
    "escalations": ["decision"],
    "deadlocks": ["decision"],
    "human_overrides": ["decision"],
}


def calculate_importance(event: dict[str, Any]) -> float:
    score = 0.0
    payload = event.get("payload", {})

    business_impact = payload.get("business_impact", 0)
    if isinstance(business_impact, (int, float)):
        score += min(business_impact, 40)

    financial_impact = payload.get("financial_impact", 0)
    if isinstance(financial_impact, (int, float)):
        score += min(abs(financial_impact) / 1000, 30)

    if event.get("actor") not in (None, "operator"):
        score += 10

    event_type = event.get("event_type", "")
    unique_events = {"deadlock", "escalation", "policy_override"}
    if event_type in unique_events:
        score += 15

    return min(score, 100.0)


def should_promote(event: dict[str, Any]) -> bool:
    event_type = event.get("event_type", "")
    promoted_types = {
        "decision_generated", "workflow_escalated", "constraint_modified",
        "decision_approved", "decision_rejected", "workflow_completed",
        "agent_unavailable",
    }
    if event_type in promoted_types:
        return True

    payload = event.get("payload", {})
    if payload.get("is_deadlock") or payload.get("is_override"):
        return True

    importance = calculate_importance(event)
    return importance >= 60.0
