from app.agents.base import BaseAgent, AgentContext, AgentRecommendation
from app.services.qwen_client import qwen
from app.services.settings import settings


class InventoryAgent(BaseAgent):
    role = "Inventory"
    model = settings.qwen_model_operational
    objectives = [
        "Check stock availability against order requirements",
        "Assess stock vs. manufacture vs. procure balance",
        "Flag stock shortages and lead time impacts",
    ]
    policies = [
        "Safety stock: maintain 10% buffer above confirmed orders",
        "Stock allocation: first-confirmed-first-served",
    ]
    tools = ["inventory_service"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += "\n\nFocus on: stock availability, quantity feasibility, stock vs. procurement recommendation."
        raw = await qwen.assess(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            response_model=AgentRecommendation,
            model=self.model,
        )
        return AgentRecommendation.model_validate(raw)
