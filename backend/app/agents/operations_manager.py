from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class OperationsManagerAgent(BaseAgent):
    role = "Operations Manager"
    model_tier = "executive"
    objectives = [
        "Synthesize all department recommendations into a coherent strategy",
        "Adjudicate conflicts between departments",
        "Ensure organizational policy compliance",
        "Make final decision with clear rationale",
    ]
    policies = [
        "Consider all department inputs before deciding",
        "Explain why alternatives were rejected",
        "Flag unresolved concerns for human operator",
        "Maintain organizational confidence above 65%",
    ]
    tools = ["policy_engine"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nYou are the Operations Manager — the executive decision-maker."
            "\nSynthesize all recommendations, resolve conflicts, and produce a final strategy."
            "\nYou must: select the best recommendation, explain your reasoning,"
            "\nlist rejected alternatives with reasons, and flag any unresolved risks."
        )
        raw = await qwen.assess_with_tools(
            system_prompt=self._build_system_prompt(),
            user_prompt=prompt,
            tools=self.get_qwen_tools(),
            response_model=AgentRecommendation,
            model=self.get_model(context),
        )
        return AgentRecommendation.model_validate(raw)
