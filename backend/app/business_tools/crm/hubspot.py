from typing import Any

from app.business_tools.base import APITool, BaseTool
from app.services.settings import settings

SIMULATED_CUSTOMERS: dict[str, dict[str, Any]] = {
    "a1b2c3d4-0001-4000-8000-000000000001": {
        "name": "Sarah Mitchell",
        "organization": "Greenfield Municipal Council",
        "segment": "government",
        "email": "sarah.mitchell@greenfield.gov",
        "total_orders": 3,
        "total_revenue_usd": 48500.00,
        "lifetime_value_usd": 142000.00,
        "payment_history": [{"date": "2026-01-15", "amount": 15000, "status": "paid"},
                            {"date": "2026-03-22", "amount": 22000, "status": "paid"},
                            {"date": "2026-05-10", "amount": 11500, "status": "paid"}],
        "open_opportunities": [{"id": "opp-001", "value": 35000, "stage": "negotiation"}],
        "preferred_client": True,
        "credit_terms": "net-60",
    },
    "a1b2c3d4-0001-4000-8000-000000000002": {
        "name": "James Okafor",
        "organization": "NovaTech Solutions",
        "segment": "enterprise",
        "email": "james.okafor@novatech.ng",
        "total_orders": 1,
        "total_revenue_usd": 8500.00,
        "lifetime_value_usd": 8500.00,
        "payment_history": [{"date": "2026-04-01", "amount": 8500, "status": "paid"}],
        "open_opportunities": [{"id": "opp-002", "value": 45000, "stage": "proposal"},
                               {"id": "opp-003", "value": 12000, "stage": "discovery"}],
        "preferred_client": False,
        "credit_terms": "50% deposit",
    },
    "a1b2c3d4-0001-4000-8000-000000000003": {
        "name": "Chioma Adeyemi",
        "organization": "RenPower Africa",
        "segment": "enterprise",
        "email": "chioma.adeyemi@renpower.africa",
        "total_orders": 5,
        "total_revenue_usd": 128000.00,
        "lifetime_value_usd": 375000.00,
        "payment_history": [{"date": "2025-09-12", "amount": 45000, "status": "paid"},
                            {"date": "2025-11-30", "amount": 32000, "status": "paid"},
                            {"date": "2026-02-18", "amount": 28000, "status": "paid"},
                            {"date": "2026-04-05", "amount": 13000, "status": "paid"},
                            {"date": "2026-06-01", "amount": 10000, "status": "paid"}],
        "open_opportunities": [{"id": "opp-004", "value": 85000, "stage": "closed_won"}],
        "preferred_client": True,
        "credit_terms": "net-30",
    },
    "a1b2c3d4-0001-4000-8000-000000000004": {
        "name": "David Chen",
        "organization": "Sunlight Initiative",
        "segment": "government",
        "email": "david.chen@sunlight.org",
        "total_orders": 2,
        "total_revenue_usd": 32000.00,
        "lifetime_value_usd": 32000.00,
        "payment_history": [{"date": "2026-03-10", "amount": 18000, "status": "paid"},
                            {"date": "2026-05-28", "amount": 14000, "status": "pending"}],
        "open_opportunities": [],
        "preferred_client": False,
        "credit_terms": "net-60",
    },
}


class HubSpotCustomerTool(APITool):
    name = "hubspot_customer"
    description = "CRM customer lookup and history via HubSpot"

    def _is_configured(self) -> bool:
        return bool(settings.hubspot_api_key)

    async def _hubspot_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        import httpx
        headers = {
            "Authorization": f"Bearer {settings.hubspot_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{settings.hubspot_base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def _find_by_email(self, email: str) -> dict[str, Any] | None:
        if not self._is_configured():
            return None
        data = await self._hubspot_request(
            "crm/v3/objects/contacts/search",
            params={"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]},
        )
        results = data.get("results", [])
        return results[0] if results else None

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "lookup_customer":
            return await self._lookup_customer(**kwargs)
        if action == "get_customer_history":
            return await self._get_customer_history(**kwargs)
        if action == "get_open_opportunities":
            return await self._get_open_opportunities(**kwargs)
        if action == "get_customer_value":
            return await self._get_customer_value(**kwargs)
        return {"error": f"Unknown action: {action}"}

    async def _lookup_customer(self, customer_id: str | None = None, email: str | None = None) -> dict[str, Any]:
        if self._is_configured() and email:
            try:
                hubspot = await self._find_by_email(email)
                if hubspot:
                    props = hubspot.get("properties", {})
                    return {
                        "status": "ok",
                        "source": "hubspot",
                        "name": props.get("firstname", "") + " " + props.get("lastname", ""),
                        "organization": props.get("company", ""),
                        "email": email,
                        "segment": "enterprise" if props.get("hs_lead_status") == "OPEN" else "standard",
                    }
            except Exception:
                pass
        customer = SIMULATED_CUSTOMERS.get(customer_id or "")
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "source": "simulated",
            "name": customer["name"],
            "organization": customer["organization"],
            "email": customer["email"],
            "segment": customer["segment"],
            "preferred_client": customer["preferred_client"],
            "credit_terms": customer["credit_terms"],
        }

    async def _get_customer_history(self, customer_id: str) -> dict[str, Any]:
        customer = SIMULATED_CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "source": "simulated",
            "customer_name": customer["name"],
            "total_orders": customer["total_orders"],
            "total_revenue_usd": customer["total_revenue_usd"],
            "payment_history": customer["payment_history"],
        }

    async def _get_open_opportunities(self, customer_id: str) -> dict[str, Any]:
        customer = SIMULATED_CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "source": "simulated",
            "customer_name": customer["name"],
            "opportunities": customer["open_opportunities"],
            "total_pipeline_value": sum(o["value"] for o in customer["open_opportunities"]),
        }

    async def _get_customer_value(self, customer_id: str) -> dict[str, Any]:
        customer = SIMULATED_CUSTOMERS.get(customer_id)
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        return {
            "status": "ok",
            "source": "simulated",
            "customer_name": customer["name"],
            "lifetime_value_usd": customer["lifetime_value_usd"],
            "segment": customer["segment"],
            "preferred_client": customer["preferred_client"],
        }


class HubSpotLookupCustomerTool(BaseTool):
    name = "lookup_customer"
    description = "Look up customer details by ID or email"

    async def execute(self, customer_id: str | None = None, email: str | None = None) -> dict[str, Any]:
        hubspot = HubSpotCustomerTool()
        return await hubspot._lookup_customer(customer_id=customer_id, email=email)


class HubSpotCustomerHistoryTool(BaseTool):
    name = "get_customer_history"
    description = "Get customer payment and order history"

    async def execute(self, customer_id: str) -> dict[str, Any]:
        hubspot = HubSpotCustomerTool()
        return await hubspot._get_customer_history(customer_id=customer_id)


class HubSpotOpportunitiesTool(BaseTool):
    name = "get_open_opportunities"
    description = "Get open sales opportunities and pipeline value for a customer"

    async def execute(self, customer_id: str) -> dict[str, Any]:
        hubspot = HubSpotCustomerTool()
        return await hubspot._get_open_opportunities(customer_id=customer_id)


class HubSpotCustomerValueTool(BaseTool):
    name = "get_customer_value"
    description = "Get customer lifetime value and segment information"

    async def execute(self, customer_id: str) -> dict[str, Any]:
        hubspot = HubSpotCustomerTool()
        return await hubspot._get_customer_value(customer_id=customer_id)
