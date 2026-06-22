from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class ProcurementDirectorAgent(BaseAgent):
    role = "Procurement Director"
    model_tier = "executive"
    objectives = [
        "Synthesize all department evaluations into coherent recommendation",
        "Adjudicate conflicts between technical, financial, and compliance assessments",
        "Ensure all regulatory and policy requirements are met",
        "Make final award recommendation with clear rationale",
    ]
    policies = [
        "Consider all department evaluations before deciding",
        "Explain why alternative vendors were rejected",
        "Flag any unresolved concerns for human procurement officer",
        "Maintain recommendation confidence above 70%",
    ]
    tools = ["policy_engine"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: cross-department synthesis, conflict adjudication,"
            " regulatory compliance, final recommendation."
        )
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
