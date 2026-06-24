import asyncio
from typing import Any

from app.agents.base import AgentContext, AgentRecommendation
from app.memory.memory_service import MemoryService
from app.workflows.loader import get_operational_workflow_agents
from app.workflows.schema import WorkflowConfig

memory_service = MemoryService()

TIER_ORDER = ["flash", "operational", "executive", "max_preview"]


def escalate_tier(current_tier: str) -> str:
    try:
        idx = TIER_ORDER.index(current_tier)
        if idx < len(TIER_ORDER) - 1:
            return TIER_ORDER[idx + 1]
    except ValueError:
        pass
    return "max_preview"


async def run_independent_assessment(
    config: WorkflowConfig,
    case_id: str,
    request_text: str,
    customer_info: dict[str, Any],
    customer_id: str | None = None,
    supplier_ids: list[str] | None = None,
    directives: list[dict[str, Any]] | None = None,
    model_tier_override: str | None = None,
    session: Any | None = None,
) -> dict[str, Any]:
    agents = get_operational_workflow_agents(config)
    if model_tier_override:
        for a in agents:
            a.model_tier = model_tier_override

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
                session=session,
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
            recommendation = await asyncio.wait_for(agent.assess(context), timeout=120.0)
            return agent.role.lower().replace(" ", "_"), recommendation, None
        except TimeoutError:
            return agent.role.lower().replace(" ", "_"), None, "Assessment timed out after 120s"
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
