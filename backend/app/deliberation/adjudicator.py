from typing import Any

from app.agents.base import AgentContext, AgentRecommendation
from app.agents.operations_manager import OperationsManagerAgent
from app.agents.registry import get_agent
from app.memory.memory_service import MemoryService

memory_service = MemoryService()


async def adjudicate(
    case_id: str,
    request_text: str,
    customer_info: dict[str, Any],
    recommendations: list[dict[str, Any]],
    challenges: list[dict[str, Any]],
    consensus: dict[str, Any],
    customer_id: str | None = None,
    supplier_ids: list[str] | None = None,
    directives: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ops_manager = get_agent("operations_manager")
    memory = await memory_service.retrieve_for_case(customer_id=customer_id, supplier_ids=supplier_ids)

    context = AgentContext(
        case_id=case_id,
        request_text=request_text,
        customer_info=customer_info,
        objectives=ops_manager.objectives,
        policies=ops_manager.policies,
        memory=memory,
        tool_outputs={
            "recommendations": recommendations,
            "challenges": challenges,
            "consensus": consensus,
        },
        directives=directives or [],
    )

    try:
        decision = await ops_manager.assess(context)
        return {
            "decision": decision.model_dump(mode="json"),
            "is_impasse": False,
            "confidence": decision.confidence,
        }
    except Exception as e:
        return {
            "decision": None,
            "is_impasse": True,
            "confidence": 0.0,
            "error": str(e),
        }
