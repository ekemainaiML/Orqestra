from app.agents.base import AgentContext, AgentRecommendation, BaseAgent
from app.services.qwen_client import qwen


class ComplianceAgent(BaseAgent):
    role = "Compliance"
    model_tier = "operational"
    objectives = [
        "Validate regulatory and statutory compliance of proposal",
        "Verify vendor certifications, licenses, and registrations",
        "Assess adherence to procurement laws and ethical standards",
        "Flag compliance risks and required remediation",
    ]
    policies = [
        "All vendors must hold valid tax clearance certificate",
        "No conflicts of interest may exist between evaluators and vendors",
        "Compliance score must be >= 0.90 for award recommendation",
    ]
    tools = ["policy_engine"]

    async def assess(self, context: AgentContext) -> AgentRecommendation:
        prompt = self._build_user_prompt(context)
        prompt += (
            "\n\nFocus on: regulatory compliance, vendor certifications,"
            " ethical standards, compliance risk assessment."
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
