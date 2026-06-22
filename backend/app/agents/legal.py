from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class LegalAgent(BaseAgent):
    role = "Legal"
    model_tier = "operational"
    objectives = [
        "Review proposed contractual terms and conditions",
        "Assess liability, indemnity, and dispute resolution provisions",
        "Verify alignment with procurement regulations and laws",
        "Recommend contract structure and special conditions",
    ]
    policies = [
        "All contracts must include standard government clauses",
        "Liability limits must not exceed prescribed thresholds",
        "Dispute resolution must specify governing law and jurisdiction",
    ]
    tools = []

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: contractual terms, liability assessment,"
            " regulatory alignment, contract structure recommendation."
        )
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
