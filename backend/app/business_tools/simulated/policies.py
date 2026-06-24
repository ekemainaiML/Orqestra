from typing import Any

from app.business_tools.base import BaseTool

POLICIES: dict[str, dict[str, Any]] = {
    "minimum_margin": {
        "id": "FIN-POL-001",
        "description": "Minimum 15% gross margin on all orders",
        "type": "hard_constraint",
        "value": 0.15,
        "department": "finance",
        "override_required": True,
    },
    "new_client_deposit": {
        "id": "FIN-POL-002",
        "description": "New clients require 50% deposit on first order",
        "type": "hard_constraint",
        "value": 0.50,
        "department": "finance",
        "override_required": True,
    },
    "government_payment_terms": {
        "id": "FIN-POL-003",
        "description": "Government clients receive net-60 payment terms",
        "type": "soft_constraint",
        "value": 60,
        "department": "finance",
        "override_required": False,
    },
    "preferred_supplier": {
        "id": "PROC-POL-001",
        "description": "Prefer suppliers with reliability score > 0.85",
        "type": "soft_constraint",
        "value": 0.85,
        "department": "procurement",
        "override_required": False,
    },
    "customs_buffer": {
        "id": "LOG-POL-001",
        "description": "Government orders: factor 3-5 days for customs clearance",
        "type": "guideline",
        "value": 5,
        "department": "logistics",
        "override_required": False,
    },
}


class CheckPolicyTool(BaseTool):
    name = "check_policy"
    description = "Check a specific policy against a business context to determine compliance"

    async def execute(self, policy_id: str, context: dict[str, Any]) -> dict[str, Any]:
        policy = POLICIES.get(policy_id)
        if not policy:
            return {"policy_id": policy_id, "found": False, "compliant": True}

        compliant = True
        details: dict[str, Any] = {}

        if policy_id == "minimum_margin":
            margin = context.get("margin_pct", 0)
            compliant = margin >= policy["value"] * 100
            details = {"margin_pct": margin, "threshold": policy["value"] * 100}
        elif policy_id == "new_client_deposit":
            is_new = context.get("is_new_client", True)
            compliant = is_new
            details = {"is_new_client": is_new, "requires_deposit": is_new}

        return {
            "policy_id": policy_id,
            "name": policy["description"],
            "type": policy["type"],
            "compliant": compliant,
            "details": details,
            "override_required": policy["override_required"] and not compliant,
        }


class GetAllPoliciesTool(BaseTool):
    name = "get_all_policies"
    description = "Get all available business policies with their descriptions and types"

    async def execute(self) -> list[dict[str, Any]]:
        return [{"id": pid, **p} for pid, p in POLICIES.items()]
