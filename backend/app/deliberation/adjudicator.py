from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, BaseAgent
from app.memory.memory_service import MemoryService

memory_service = MemoryService()


def _check_hard_constraints(
    policies: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for policy in policies:
        if not policy.get("hard_constraint", False):
            continue
        policy_id = policy.get("id", "unknown")
        rule = policy.get("rule", "")
        for rec in recommendations:
            rec_text = f"{rec.get('recommendation', '')} {rec.get('reasoning', '')} {rec.get('risks', [])}"
            rec_text = rec_text.lower()
            if policy_id == "minimum_margin" and "margin" in rec_text:
                for token in rec_text.split():
                    if "%" in token:
                        try:
                            val = float(token.replace("%", ""))
                            if val < 15:
                                violations.append({
                                    "policy_id": policy_id,
                                    "rule": rule,
                                    "agent": rec.get("agent_id", "unknown"),
                                    "detail": f"Margin {val}% below 15% minimum",
                                })
                        except ValueError:
                            pass
        if policy_id == "budget_compliance" and "budget" in rec_text:
            violations.append({
                "policy_id": policy_id,
                "rule": rule,
                "agent": rec.get("agent_id", "unknown"),
                "detail": "Budget compliance requires explicit confirmation",
            })
    return violations


async def adjudicate(
    executive_agent: BaseAgent,
    case_id: str,
    request_text: str,
    customer_info: dict[str, Any],
    recommendations: list[dict[str, Any]],
    challenges: list[dict[str, Any]],
    consensus: dict[str, Any],
    customer_id: str | None = None,
    supplier_ids: list[str] | None = None,
    directives: list[dict[str, Any]] | None = None,
    policies: list[dict[str, Any]] | None = None,
    model_tier_override: str | None = None,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    if model_tier_override:
        executive_agent.model_tier = model_tier_override

    policy_defs = policies or []
    violations = _check_hard_constraints(policy_defs, recommendations)

    memory = await memory_service.retrieve_for_case(customer_id=customer_id, supplier_ids=supplier_ids, session=session)

    context = AgentContext(
        case_id=case_id,
        request_text=request_text,
        customer_info=customer_info,
        objectives=executive_agent.objectives,
        policies=executive_agent.policies,
        memory=memory,
        tool_outputs={
            "recommendations": recommendations,
            "challenges": challenges,
            "consensus": consensus,
            "policies": policy_defs,
            "policy_violations": violations,
        },
        directives=directives or [],
    )

    try:
        decision = await executive_agent.assess(context)
        return {
            "decision": decision.model_dump(mode="json"),
            "is_impasse": False,
            "confidence": decision.confidence,
            "policy_violations": violations,
        }
    except Exception as e:
        return {
            "decision": None,
            "is_impasse": True,
            "confidence": 0.0,
            "error": str(e),
            "policy_violations": violations,
        }
