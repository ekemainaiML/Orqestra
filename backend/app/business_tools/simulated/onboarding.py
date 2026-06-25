from typing import Any

from app.business_tools.base import BaseTool

CUSTOMERS: dict[str, dict[str, Any]] = {
    "a1b2c3d4-0001-4000-8000-000000000001": {
        "name": "Sarah Mitchell",
        "organization": "Greenfield Municipal Council",
        "segment": "government",
        "kyc_status": "verified",
        "credit_score": 82,
        "docs_submitted": ["business_license", "tax_clearance", "proof_of_address"],
        "docs_missing": ["signatory_authorization"],
        "onboarding_priority": "standard",
    },
    "a1b2c3d4-0001-4000-8000-000000000002": {
        "name": "James Okafor",
        "organization": "NovaTech Solutions",
        "segment": "enterprise",
        "kyc_status": "pending",
        "credit_score": 74,
        "docs_submitted": ["business_license", "proof_of_address"],
        "docs_missing": ["tax_clearance", "signatory_authorization", "financial_statements"],
        "onboarding_priority": "high",
    },
    "a1b2c3d4-0001-4000-8000-000000000003": {
        "name": "Chioma Adeyemi",
        "organization": "RenPower Africa",
        "segment": "enterprise",
        "kyc_status": "verified",
        "credit_score": 91,
        "docs_submitted": [
            "business_license", "tax_clearance", "proof_of_address",
            "signatory_authorization", "financial_statements",
        ],
        "docs_missing": [],
        "onboarding_priority": "high",
    },
    "a1b2c3d4-0001-4000-8000-000000000004": {
        "name": "David Chen",
        "organization": "Sunlight Initiative",
        "segment": "government",
        "kyc_status": "verified",
        "credit_score": 88,
        "docs_submitted": ["business_license", "tax_clearance", "proof_of_address", "signatory_authorization"],
        "docs_missing": [],
        "onboarding_priority": "standard",
    },
}


class CheckKycTool(BaseTool):
    name = "check_kyc"
    description = "Check KYC status and customer segment information"

    async def execute(self, customer_id: str) -> dict[str, Any]:  # type: ignore[override]
        customer = CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "customer_name": customer["name"],
            "organization": customer["organization"],
            "kyc_status": customer["kyc_status"],
            "segment": customer["segment"],
        }


class CheckCreditTool(BaseTool):
    name = "check_credit"
    description = "Check customer credit score and determine if deposit is required"

    async def execute(self, customer_id: str) -> dict[str, Any]:  # type: ignore[override]
        customer = CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        score = customer["credit_score"]
        return {
            "status": "ok",
            "customer_name": customer["name"],
            "credit_score": score,
            "rating": "excellent" if score >= 85 else "good" if score >= 70 else "fair",
            "requires_deposit": score < 75,
        }


class VerifyDocumentsTool(BaseTool):
    name = "verify_documents"
    description = "Verify customer documentation completeness for onboarding"

    async def execute(self, customer_id: str) -> dict[str, Any]:  # type: ignore[override]
        customer = CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "customer_name": customer["name"],
            "documents_submitted": customer["docs_submitted"],
            "documents_missing": customer["docs_missing"],
            "all_documents_verified": len(customer["docs_missing"]) == 0,
            "readiness": "ready" if len(customer["docs_missing"]) == 0 else "incomplete",
        }
