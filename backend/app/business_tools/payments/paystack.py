from typing import Any

from app.business_tools.base import BaseTool
from app.services.settings import settings

SIMULATED_TRANSACTIONS: dict[str, list[dict[str, Any]]] = {
    "a1b2c3d4-0001-4000-8000-000000000001": [
        {"reference": "TXN-001", "amount": 15000.00, "currency": "USD", "status": "success",
         "date": "2026-01-15", "channel": "bank_transfer"},
        {"reference": "TXN-002", "amount": 22000.00, "currency": "USD", "status": "success",
         "date": "2026-03-22", "channel": "card"},
        {"reference": "TXN-003", "amount": 11500.00, "currency": "USD", "status": "success",
         "date": "2026-05-10", "channel": "bank_transfer"},
    ],
    "a1b2c3d4-0001-4000-8000-000000000002": [
        {"reference": "TXN-004", "amount": 8500.00, "currency": "USD", "status": "success",
         "date": "2026-04-01", "channel": "card"},
        {"reference": "TXN-005", "amount": 4500.00, "currency": "USD", "status": "failed",
         "date": "2026-05-20", "channel": "card", "failure_reason": "insufficient_funds"},
    ],
    "a1b2c3d4-0001-4000-8000-000000000003": [
        {"reference": "TXN-006", "amount": 45000.00, "currency": "USD", "status": "success",
         "date": "2025-09-12", "channel": "bank_transfer"},
        {"reference": "TXN-007", "amount": 32000.00, "currency": "USD", "status": "success",
         "date": "2025-11-30", "channel": "bank_transfer"},
        {"reference": "TXN-008", "amount": 28000.00, "currency": "USD", "status": "success",
         "date": "2026-02-18", "channel": "card"},
        {"reference": "TXN-009", "amount": 13000.00, "currency": "USD", "status": "success",
         "date": "2026-04-05", "channel": "bank_transfer"},
        {"reference": "TXN-010", "amount": 10000.00, "currency": "USD", "status": "success",
         "date": "2026-06-01", "channel": "card"},
    ],
    "a1b2c3d4-0001-4000-8000-000000000004": [
        {"reference": "TXN-011", "amount": 18000.00, "currency": "USD", "status": "success",
         "date": "2026-03-10", "channel": "bank_transfer"},
        {"reference": "TXN-012", "amount": 14000.00, "currency": "USD", "status": "pending",
         "date": "2026-05-28", "channel": "card"},
    ],
}

SIMULATED_CUSTOMER_SCORES: dict[str, dict[str, Any]] = {
    "a1b2c3d4-0001-4000-8000-000000000001": {
        "customer_id": "a1b2c3d4-0001-4000-8000-000000000001",
        "name": "Sarah Mitchell",
        "credit_score": 82,
        "payment_reliability": 1.0,
        "total_transactions": 3,
        "failed_transactions": 0,
        "avg_days_to_pay": 28,
        "risk_level": "low",
    },
    "a1b2c3d4-0001-4000-8000-000000000002": {
        "customer_id": "a1b2c3d4-0001-4000-8000-000000000002",
        "name": "James Okafor",
        "credit_score": 74,
        "payment_reliability": 0.5,
        "total_transactions": 2,
        "failed_transactions": 1,
        "avg_days_to_pay": 35,
        "risk_level": "medium",
    },
    "a1b2c3d4-0001-4000-8000-000000000003": {
        "customer_id": "a1b2c3d4-0001-4000-8000-000000000003",
        "name": "Chioma Adeyemi",
        "credit_score": 91,
        "payment_reliability": 1.0,
        "total_transactions": 5,
        "failed_transactions": 0,
        "avg_days_to_pay": 21,
        "risk_level": "low",
    },
    "a1b2c3d4-0001-4000-8000-000000000004": {
        "customer_id": "a1b2c3d4-0001-4000-8000-000000000004",
        "name": "David Chen",
        "credit_score": 88,
        "payment_reliability": 0.5,
        "total_transactions": 2,
        "failed_transactions": 0,
        "avg_days_to_pay": 42,
        "risk_level": "low",
    },
}


class PaystackAPITool:
    """Payment processing backend via Paystack (utility, not a registered tool)"""

    def _is_configured(self) -> bool:
        return bool(settings.paystack_secret_key)

    async def _paystack_request(self, endpoint: str) -> dict[str, Any]:
        import httpx
        headers = {
            "Authorization": f"Bearer {settings.paystack_secret_key}",
            "Content-Type": "application/json",
        }
        url = f"https://api.paystack.co/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()


class VerifyPaymentTool(BaseTool):
    name = "verify_payment"
    description = "Verify a payment transaction by reference code"

    async def execute(self, reference: str) -> dict[str, Any]:  # type: ignore[override]
        if settings.paystack_secret_key:
            try:
                paystack = PaystackAPITool()
                data = await paystack._paystack_request(f"transaction/verify/{reference}")
                tx = data.get("data", {})
                return {
                    "status": "ok",
                    "source": "paystack",
                    "reference": reference,
                    "amount": tx.get("amount", 0) / 100,
                    "currency": tx.get("currency", "NGN"),
                    "payment_status": tx.get("status", "unknown"),
                    "channel": tx.get("channel", ""),
                    "paid_at": tx.get("paid_at", ""),
                }
            except Exception:
                pass

        for txns in SIMULATED_TRANSACTIONS.values():
            for t in txns:
                if t["reference"] == reference:
                    return {
                        "status": "ok",
                        "source": "simulated",
                        "reference": reference,
                        "amount": t["amount"],
                        "currency": t["currency"],
                        "payment_status": t["status"],
                        "channel": t["channel"],
                        "failure_reason": t.get("failure_reason"),
                    }
        return {"status": "error", "message": f"Transaction not found: {reference}"}


class CheckTransactionHistoryTool(BaseTool):
    name = "check_transaction_history"
    description = "Check transaction history for a customer"

    async def execute(self, customer_id: str) -> dict[str, Any]:  # type: ignore[override]
        txns = SIMULATED_TRANSACTIONS.get(customer_id)
        if not txns:
            return {"status": "error", "message": "Customer not found"}
        successful = [t for t in txns if t["status"] == "success"]
        failed = [t for t in txns if t["status"] == "failed"]
        pending = [t for t in txns if t["status"] == "pending"]
        total_volume = sum(t["amount"] for t in successful)
        return {
            "status": "ok",
            "source": "simulated",
            "total_transactions": len(txns),
            "successful": len(successful),
            "failed": len(failed),
            "pending": len(pending),
            "total_volume_usd": round(total_volume, 2),
            "transactions": txns,
        }


class AssessCreditRiskTool(BaseTool):
    name = "assess_credit_risk"
    description = "Assess credit risk for a customer based on payment history"

    async def execute(self, customer_id: str) -> dict[str, Any]:  # type: ignore[override]
        score = SIMULATED_CUSTOMER_SCORES.get(customer_id)
        if not score:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "source": "simulated",
            "customer_name": score["name"],
            "credit_score": score["credit_score"],
            "payment_reliability": score["payment_reliability"],
            "total_transactions": score["total_transactions"],
            "failed_transactions": score["failed_transactions"],
            "avg_days_to_pay": score["avg_days_to_pay"],
            "risk_level": score["risk_level"],
            "recommended_deposit": score["risk_level"] == "medium",
        }


class RecommendPaymentTermsTool(BaseTool):
    name = "recommend_payment_terms"
    description = "Recommend payment terms based on customer history and risk profile"

    async def execute(  # type: ignore[override]
            self, customer_id: str, requested_terms: str | None = None,
            amount: float | None = None) -> dict[str, Any]:
        score = SIMULATED_CUSTOMER_SCORES.get(customer_id)
        if not score:
            return {"status": "error", "message": "Customer not found"}

        if score["risk_level"] == "low" and score["payment_reliability"] >= 0.8:
            terms = "net-60"
            requires_deposit = False
            deposit_pct = 0
        elif score["risk_level"] == "medium":
            terms = "50% deposit, balance net-30"
            requires_deposit = True
            deposit_pct = 50
        else:
            terms = "100% upfront payment"
            requires_deposit = True
            deposit_pct = 100

        return {
            "status": "ok",
            "source": "simulated",
            "customer_name": score["name"],
            "recommended_terms": terms,
            "requires_deposit": requires_deposit,
            "deposit_percentage": deposit_pct,
            "risk_level": score["risk_level"],
            "credit_score": score["credit_score"],
            "requested_terms": requested_terms,
        }
