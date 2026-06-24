from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class ProcurementAgent(BaseAgent):
    role = "Procurement"
    model_tier = "operational"
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
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
            on_tool_call=self._make_tool_callback(context),
        )
        return AgentRecommendation.model_validate(raw)
