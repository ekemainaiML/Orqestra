from typing import Any


async def check_availability(product: str, quantity: int) -> dict[str, Any]:
    stock = {
        "solar_street_light_60w": 200,
        "solar_street_light_100w": 150,
        "solar_panel_300w": 300,
        "battery_12v_100ah": 250,
        "charge_controller_30a": 180,
    }
    available = stock.get(product, 0)
    return {
        "product": product,
        "requested": quantity,
        "available": available,
        "shortfall": max(0, quantity - available),
        "needs_procurement": quantity > available,
        "safety_stock_after": max(0, available - quantity),
    }


async def get_product_specs(product: str) -> dict[str, Any]:
    specs = {
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
    return specs.get(product, {})
