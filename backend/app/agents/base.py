from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field

from app.business_tools.definitions import get_tool_definitions, get_tool_names_for_agent
from app.services.settings import settings


class AgentRecommendation(BaseModel):
    agent_id: str
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    risks: list[str] = []
    alternatives: list[str] = []
    evidence: list[dict[str, Any]] = []


class Challenge(BaseModel):
    challenge_id: str
    source_agent: str
    target_agent: str
    challenge_type: str
    statement: str
    evidence: list[dict[str, Any]]
    confidence: float = Field(ge=0.0, le=1.0)


class AgentContext(BaseModel):
    case_id: str
    request_text: str
    customer_info: dict[str, Any]
    objectives: list[str]
    policies: list[str]
    memory: list[dict[str, Any]]
    tool_outputs: dict[str, Any]
    directives: list[dict[str, Any]] = []


MODEL_TIERS: dict[str, str] = {
    "flash": settings.qwen_model_flash,
    "operational": settings.qwen_model_operational,
    "executive": settings.qwen_model_executive,
    "max_preview": settings.qwen_model_max_preview,
}


def resolve_model(model_or_tier: str) -> str:
    return MODEL_TIERS.get(model_or_tier, model_or_tier)


class BaseAgent(ABC):
    role: str
    model: str = ""
    model_tier: str = "operational"
    objectives: list[str] = []
    policies: list[str] = []
    tools: list[str] = []

    def get_model(self, context: AgentContext | None = None) -> str:
        if self.model:
            return self.model
        return resolve_model(self.model_tier)

    def get_escalated_model(self) -> str:
        escalation_chain = ["flash", "operational", "executive", "max_preview"]
        try:
            idx = escalation_chain.index(self.model_tier)
            if idx < len(escalation_chain) - 1:
                return resolve_model(escalation_chain[idx + 1])
        except ValueError:
            pass
        return resolve_model("max_preview")

    def get_qwen_tools(self) -> list[dict[str, Any]]:
        tool_names = get_tool_names_for_agent(self.tools)
        return get_tool_definitions(tool_names)

    def _make_tool_callback(
        self, context: AgentContext
    ) -> Callable[[str, dict[str, Any], Any], Awaitable[None]]:
        async def _on_call(fn_name: str, fn_args: dict[str, Any], result: Any) -> None:
            from app.events.publisher import publish_event
            await publish_event(
                case_id=context.case_id,
                event_type="tool_call_executed",
                actor=self.role,
                payload={"tool": fn_name, "arguments": fn_args, "result": result},
            )
        return _on_call

    @abstractmethod
    async def assess(self, context: AgentContext) -> AgentRecommendation:
        ...

    def _build_system_prompt(self) -> str:
        prompt = (
            f"You are the {self.role} department in an AI organization called Orqestra.\n"
            f"Your objectives: {', '.join(self.objectives)}\n"
            f"Policies you must follow: {', '.join(self.policies)}\n"
        )
        qwen_tools = self.get_qwen_tools()
        if qwen_tools:
            tool_names = [t["function"]["name"] for t in qwen_tools]
            prompt += f"Tools available: {', '.join(tool_names)}\n"
        else:
            prompt += f"Tools available: {', '.join(self.tools)}\n"
        prompt += "You communicate in structured JSON. Think in natural language, respond in contracts.\n"
        prompt += (
            "You have access to function calls. When you need information, "
            "call the appropriate function instead of guessing. "
            "After gathering all necessary data, produce your final recommendation."
        )
        return prompt

    def _build_user_prompt(self, context: AgentContext) -> str:
        memory_section = ""
        if context.memory:
            entries = "\n".join(
                f"- [{m.get('memory_type','memory')}] {m.get('content',{}).get('summary','')}"
                for m in context.memory
            )
            memory_section = f"\nOrganizational memory retrieved:\n{entries}\n"

        tools_section = ""
        if context.tool_outputs:
            tools_section = f"\nPre-computed tool results:\n{context.tool_outputs}\n"

        directives_section = ""
        if context.directives:
            directives_section = f"\nActive strategic directives:\n{context.directives}\n"

        return (
            f"Case: {context.request_text}\n"
            f"Customer: {context.customer_info}\n"
            f"{memory_section}"
            f"{tools_section}"
            f"{directives_section}"
            "\nProvide your recommendation as JSON with fields: "
            "recommendation, confidence, reasoning, risks, alternatives, evidence."
        )
