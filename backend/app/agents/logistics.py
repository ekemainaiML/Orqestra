from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen
from app.services.settings import settings


class LogisticsAgent(BaseAgent):
    role = "Logistics"
    model = settings.qwen_model_operational
    objectives = [
        "Validate delivery feasibility within requested timeline",
        "Assess shipping routes and costs",
        "Identify delivery risks (customs, distance, weather)",
        "Recommend optimal shipping strategy",
    ]
    policies = [
        "Government orders: factor 3-5 days for customs clearance",
        "International shipping requires minimum 7-day lead time",
        "Regional delivery within 3 days available for Africa-based suppliers",
    ]
    tools = ["supplier_db"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += "\n\nFocus on: delivery feasibility, timeline assessment, shipping risks, logistics recommendation."
        raw = await qwen.assess(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            response_model=AgentRecommendation,
            model=self.model,
        )
        return AgentRecommendation.model_validate(raw)
