from typing import Any

from app.business_tools.base import BaseTool

BASE_UNIT_PRICE = 195.00
VOLUME_DISCOUNT_THRESHOLD = 250
VOLUME_DISCOUNT_RATE = 0.10
PREFERRED_CLIENT_DISCOUNT = 0.05


class CalculatePriceTool(BaseTool):
    name = "calculate_price"
    description = "Calculate unit price, subtotal, margin and applicable discounts"

    async def execute(self, quantity: int, is_preferred: bool = False, is_government: bool = False) -> dict[str, Any]:
        unit_price = BASE_UNIT_PRICE
        if quantity >= VOLUME_DISCOUNT_THRESHOLD:
            unit_price *= (1 - VOLUME_DISCOUNT_RATE)
        if is_preferred:
            unit_price *= (1 - PREFERRED_CLIENT_DISCOUNT)
        subtotal = unit_price * quantity
        margin = unit_price - 120.00
        margin_pct = margin / unit_price
        return {
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "subtotal": round(subtotal, 2),
            "estimated_margin_pct": round(margin_pct * 100, 1),
            "volume_discount_applied": quantity >= VOLUME_DISCOUNT_THRESHOLD,
            "preferred_discount_applied": is_preferred,
        }


class GetExchangeRateTool(BaseTool):
    name = "get_exchange_rate"
    description = "Get simulated exchange rate between two currencies"

    async def execute(self, base: str = "USD", target: str = "NGN") -> dict[str, Any]:
        rates = {"USD_NGN": 1550.0, "USD_KES": 130.0}
        return {
            "pair": f"{base}_{target}",
            "rate": rates.get(f"{base}_{target}", 1.0),
            "source": "simulated",
        }
