from typing import Any

SUPPLIERS: dict[str, dict[str, Any]] = {
    "solartech": {
        "id": "b2c3d4e5-0001-4000-8000-000000000001",
        "name": "SolarTech Manufacturing",
        "region": "Asia",
        "lead_time_days": 10,
        "reliability_score": 0.92,
        "min_order_qty": 100,
        "unit_price_usd": 180.00,
        "payment_terms": "30% deposit, 70% on shipment",
    },
    "brightpath": {
        "id": "b2c3d4e5-0001-4000-8000-000000000002",
        "name": "BrightPath Solar Co.",
        "region": "Asia",
        "lead_time_days": 7,
        "reliability_score": 0.78,
        "min_order_qty": 250,
        "unit_price_usd": 155.00,
        "payment_terms": "50% deposit, 50% on delivery",
    },
    "afrienergy": {
        "id": "b2c3d4e5-0001-4000-8000-000000000003",
        "name": "AfriEnergy Components",
        "region": "Africa",
        "lead_time_days": 5,
        "reliability_score": 0.85,
        "min_order_qty": 50,
        "unit_price_usd": 210.00,
        "payment_terms": "Net-30",
    },
}


async def find_suppliers(region: str | None = None, min_reliability: float = 0.0) -> list[dict[str, Any]]:
    results = []
    for s in SUPPLIERS.values():
        if region and s["region"].lower() != region.lower():
            continue
        if s["reliability_score"] < min_reliability:
            continue
        results.append(s)
    return sorted(results, key=lambda x: x["reliability_score"], reverse=True)


async def get_supplier(supplier_id: str) -> dict[str, Any] | None:
    for s in SUPPLIERS.values():
        if s["id"] == supplier_id:
            return s
    return None
