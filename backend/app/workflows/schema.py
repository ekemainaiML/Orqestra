from typing import Any

from pydantic import BaseModel, Field


class DepartmentConfig(BaseModel):
    id: str
    role: str
    model_tier: str = "operational"
    objectives: list[str] = []
    policies: list[str] = []
    tools: list[str] = []


class PolicyConfig(BaseModel):
    id: str
    rule: str
    hard_constraint: bool = False


class GovernanceConfig(BaseModel):
    challenge_round: bool = True
    consensus_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    deadlock_resolution: str = "escalate"


class ApprovalConfig(BaseModel):
    required_role: str = "operations_manager"
    auto_approve_confidence: float = Field(default=0.95, ge=0.0, le=1.0)


class WorkflowConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    departments: list[DepartmentConfig]
    decision_dimensions: list[str] = []
    governance: GovernanceConfig = GovernanceConfig()
    policies: list[PolicyConfig] = []
    approval: ApprovalConfig = ApprovalConfig()

    def get_operational_departments(self) -> list[DepartmentConfig]:
        return [d for d in self.departments if d.id != self.approval.required_role]

    def get_executive_department(self) -> DepartmentConfig | None:
        for d in self.departments:
            if d.id == self.approval.required_role:
                return d
        return None

    def get_critical_department_ids(self) -> list[str]:
        return [d.id for d in self.departments if d.model_tier != "flash"]

    def model_dump_flat(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "departments": [d.model_dump() for d in self.departments],
            "decision_dimensions": self.decision_dimensions,
            "consensus_threshold": self.governance.consensus_threshold,
            "policies": [p.model_dump() for p in self.policies],
            "required_role": self.approval.required_role,
        }
