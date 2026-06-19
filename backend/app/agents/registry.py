from app.agents.base import BaseAgent
from app.agents.sales import SalesAgent
from app.agents.finance import FinanceAgent
from app.agents.inventory import InventoryAgent
from app.agents.procurement import ProcurementAgent
from app.agents.logistics import LogisticsAgent
from app.agents.operations_manager import OperationsManagerAgent

_registry: dict[str, type[BaseAgent]] = {
    "sales": SalesAgent,
    "finance": FinanceAgent,
    "inventory": InventoryAgent,
    "procurement": ProcurementAgent,
    "logistics": LogisticsAgent,
    "operations_manager": OperationsManagerAgent,
}


def get_agent(agent_id: str) -> BaseAgent:
    cls = _registry.get(agent_id)
    if cls is None:
        raise ValueError(f"Unknown agent: {agent_id}")
    return cls()


def get_agents_for_workflow(workflow_type: str) -> list[BaseAgent]:
    if workflow_type == "order_fulfillment":
        return [get_agent(aid) for aid in ["sales", "inventory", "procurement", "finance", "logistics", "operations_manager"]]
    raise ValueError(f"Unknown workflow type: {workflow_type}")


def get_operational_agents(workflow_type: str) -> list[BaseAgent]:
    return [a for a in get_agents_for_workflow(workflow_type) if a.role != "Operations Manager"]


def get_all_agent_ids() -> list[str]:
    return list(_registry.keys())


def get_critical_agent_ids() -> list[str]:
    return ["finance", "inventory", "logistics"]


def get_non_critical_agent_ids() -> list[str]:
    return ["sales", "procurement"]
