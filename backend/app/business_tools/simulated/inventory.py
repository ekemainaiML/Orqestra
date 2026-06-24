from typing import Any

from app.business_tools.base import BaseTool

STOCK: dict[str, int] = {
    "solar_street_light_60w": 200,
    "solar_street_light_100w": 150,
    "solar_panel_300w": 300,
    "battery_12v_100ah": 250,
    "charge_controller_30a": 180,
}

SPECS: dict[str, dict[str, Any]] = {
    "solar_street_light_60w": {
        "wattage": 60,
        "lumens": 7200,
        "battery_capacity": "12V 60Ah",
        "solar_panel": "75W poly",
        "lifespan_hours": 50000,
    },
    "solar_street_light_100w": {
        "wattage": 100,
        "lumens": 12000,
        "battery_capacity": "12V 100Ah",
        "solar_panel": "120W poly",
        "lifespan_hours": 50000,
    },
}


class CheckAvailabilityTool(BaseTool):
    name = "check_availability"
    description = "Check current stock availability for a product"

    async def execute(self, product: str, quantity: int) -> dict[str, Any]:
        available = STOCK.get(product, 0)
        return {
            "product": product,
            "requested": quantity,
            "available": available,
            "shortfall": max(0, quantity - available),
            "needs_procurement": quantity > available,
            "safety_stock_after": max(0, available - quantity),
        }


class GetProductSpecsTool(BaseTool):
    name = "get_product_specs"
    description = "Get technical specifications for a product"

    async def execute(self, product: str) -> dict[str, Any]:
        return SPECS.get(product, {})
