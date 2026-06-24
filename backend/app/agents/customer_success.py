from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class CustomerSuccessAgent(BaseAgent):
    role = "Customer Success"
    model_tier = "operational"
    objectives = [
        "Assess customer readiness for onboarding",
        "Verify documentation and KYC completeness",
        "Identify training and support requirements",
        "Recommend onboarding timeline and plan",
    ]
    policies = [
        "All customers must complete KYC before onboarding",
        "New customers require onboarding within 14 business days",
        "Enterprise customers get dedicated success manager",
    ]
    tools = ["onboarding_service"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: customer readiness, documentation completeness,"
            " training needs, onboarding plan recommendation."
        )
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
            on_tool_call=self._make_tool_callback(context),
        )
        return AgentRecommendation.model_validate(raw)
