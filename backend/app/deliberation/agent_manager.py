import asyncio
from typing import Any

from app.agents.base import AgentContext, AgentRecommendation
from app.agents.registry import get_operational_agents
from app.memory.memory_service import MemoryService

memory_service = MemoryService()


async def run_independent_assessment(
    case_id: str,
    request_text: str,
    customer_info: dict[str, Any],
    customer_id: str | None = None,
    supplier_ids: list[str] | None = None,
    directives: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    agents = get_operational_agents("order_fulfillment")
    results: dict[str, Any] = {
        "recommendations": [],
        "unavailable_agents": [],
        "agent_responses": {},
    }

    async def assess_agent(agent: Any) -> tuple[str, AgentRecommendation | None, str | None]:
        try:
            memory = await memory_service.retrieve_for_agent(
                agent_id=agent.role.lower().replace(" ", "_"),
                department=agent.role.lower(),
                customer_id=customer_id,
                supplier_ids=supplier_ids,
            )
            context = AgentContext(
                case_id=case_id,
                request_text=request_text,
                customer_info=customer_info,
                objectives=agent.objectives,
                policies=agent.policies,
                memory=memory,
                tool_outputs={},
                directives=directives or [],
            )
            recommendation = await agent.assess(context)
            return agent.role.lower().replace(" ", "_"), recommendation, None
        except Exception as e:
            return agent.role.lower().replace(" ", "_"), None, str(e)

    tasks = [assess_agent(agent) for agent in agents]
    completed = await asyncio.gather(*tasks)

    for agent_id, recommendation, error in completed:
        if error:
            results["unavailable_agents"].append({"agent_id": agent_id, "error": error})
        elif recommendation:
            results["recommendations"].append(recommendation.model_dump(mode="json"))
            results["agent_responses"][agent_id] = recommendation.model_dump(mode="json")

    return results
