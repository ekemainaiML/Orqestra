from app.agents.base import BaseAgent
from app.agents.compliance import ComplianceAgent
from app.agents.finance import FinanceAgent
from app.agents.inventory import InventoryAgent
from app.agents.legal import LegalAgent
from app.agents.logistics import LogisticsAgent
from app.agents.operations_manager import OperationsManagerAgent
from app.agents.procurement import ProcurementAgent
from app.agents.procurement_director import ProcurementDirectorAgent
from app.agents.procurement_review import ProcurementReviewAgent
from app.agents.sales import SalesAgent
from app.agents.technical_evaluation import TechnicalEvaluationAgent

_registry: dict[str, type[BaseAgent]] = {
    "sales": SalesAgent,
    "finance": FinanceAgent,
    "inventory": InventoryAgent,
    "procurement": ProcurementAgent,
    "logistics": LogisticsAgent,
    "operations_manager": OperationsManagerAgent,
    "procurement_review": ProcurementReviewAgent,
    "technical_evaluation": TechnicalEvaluationAgent,
    "compliance": ComplianceAgent,
    "legal": LegalAgent,
    "procurement_director": ProcurementDirectorAgent,
}


def get_agent_class(agent_id: str) -> type[BaseAgent]:
    cls = _registry.get(agent_id)
    if cls is None:
        raise ValueError(f"Unknown agent: {agent_id}")
    return cls


def get_agent(agent_id: str) -> BaseAgent:
    return get_agent_class(agent_id)()


def get_all_agent_ids() -> list[str]:
    return list(_registry.keys())
