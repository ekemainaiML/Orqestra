from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class FinanceAgent(BaseAgent):
    role = "Finance"
    model_tier = "operational"
    objectives = [
        "Evaluate deal profitability and margin",
        "Assess financial risk and payment terms",
        "Ensure policy compliance (minimum margin, payment terms)",
        "Recommend optimal pricing structure",
    ]
    policies = [
        "Minimum 15% gross margin on all orders",
        "International contracts must account for currency risk",
        "New clients: 50% deposit required for first order",
    ]
    tools = ["pricing_engine", "policy_engine"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += "\n\nFocus on: margin analysis, financial risk, policy compliance, pricing recommendation."
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
