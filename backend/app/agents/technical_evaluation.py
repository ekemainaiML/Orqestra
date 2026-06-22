from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class TechnicalEvaluationAgent(BaseAgent):
    role = "Technical Evaluation"
    model_tier = "operational"
    objectives = [
        "Assess technical proposal quality against tender specifications",
        "Verify vendor capability to deliver specified requirements",
        "Identify technical risks and mitigation strategies",
        "Score technical compliance and innovation",
    ]
    policies = [
        "Technical proposal must meet or exceed all mandatory specifications",
        "Substitution of specified materials requires approval",
        "Warranty and support terms must meet minimum standards",
    ]
    tools = []

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += "\n\nFocus on: technical proposal quality, specification compliance, delivery capability, technical risk assessment."
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
