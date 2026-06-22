from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class ProcurementReviewAgent(BaseAgent):
    role = "Procurement Review"
    model_tier = "operational"
    objectives = [
        "Evaluate vendor suitability against tender requirements",
        "Verify tender documentation completeness and compliance",
        "Assess procurement history and past performance",
        "Recommend vendor selection with supporting evidence",
    ]
    policies = [
        "Prefer vendors with proven track record in public sector contracts",
        "All tender submissions must meet minimum compliance threshold of 0.85",
        "Local content preference applies where regulations require",
    ]
    tools = ["supplier_db"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: vendor suitability, tender compliance,"
            " procurement history, vendor selection recommendation."
        )
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
