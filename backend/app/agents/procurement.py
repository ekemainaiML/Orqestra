from app.agents.base import BaseAgent, AgentContext, AgentRecommendation
from app.services.qwen_client import qwen
from app.services.settings import settings


class ProcurementAgent(BaseAgent):
    role = "Procurement"
    model = settings.qwen_model_operational
    objectives = [
        "Identify optimal supplier based on cost, reliability, and lead time",
        "Evaluate sourcing options (local vs international)",
        "Assess supplier risk and historical performance",
        "Recommend procurement strategy",
    ]
    policies = [
        "Prefer suppliers with proven reliability score > 0.85",
        "International orders require currency risk assessment",
        "Regional suppliers prioritized for urgent orders",
    ]
    tools = ["supplier_db"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += "\n\nFocus on: supplier selection, sourcing strategy, cost analysis, lead time assessment."
        raw = await qwen.assess(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            response_model=AgentRecommendation,
            model=self.model,
        )
        return AgentRecommendation.model_validate(raw)
