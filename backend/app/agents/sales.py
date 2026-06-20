from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen
from app.services.settings import settings


class SalesAgent(BaseAgent):
    role = "Sales"
    model = settings.qwen_model_operational
    objectives = [
        "Interpret customer intent and requirements",
        "Generate accurate quotations",
        "Identify upselling opportunities",
        "Assess customer relationship history",
    ]
    policies = [
        "Standard pricing applies unless volume discount authorized",
        "First-time customers require full upfront payment",
        "Government clients get net-60 terms standard",
    ]
    tools = ["pricing_engine", "customer_db"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: customer intent, quotation recommendation, "
            "upselling opportunities, relationship assessment."
        )
        raw = await qwen.assess(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            response_model=AgentRecommendation,
            model=self.model,
        )
        return AgentRecommendation.model_validate(raw)
