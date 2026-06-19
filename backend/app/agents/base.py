from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


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


class BaseAgent(ABC):
    role: str
    model: str
    objectives: list[str] = []
    policies: list[str] = []
    tools: list[str] = []

    @abstractmethod
    async def assess(self, context: AgentContext) -> AgentRecommendation:
        ...

    def _build_system_prompt(self) -> str:
        return (
            f"You are the {self.role} department in an AI organization called Orqestra.\n"
            f"Your objectives: {', '.join(self.objectives)}\n"
            f"Policies you must follow: {', '.join(self.policies)}\n"
            f"Tools available: {', '.join(self.tools)}\n"
            "You communicate in structured JSON. Think in natural language, respond in contracts."
        )

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
            tools_section = f"\nTool results:\n{context.tool_outputs}\n"

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
