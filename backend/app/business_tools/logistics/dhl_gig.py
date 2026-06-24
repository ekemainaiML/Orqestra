from typing import Any

from app.business_tools.base import APITool, BaseTool
from app.services.settings import settings

SIMULATED_ROUTES: dict[str, dict[str, Any]] = {
    "LAG-ACC": {
        "origin": "Lagos, Nigeria",
        "destination": "Accra, Ghana",
        "mode": "road",
        "distance_km": 680,
        "transit_days": 4,
        "cost_usd_per_kg": 3.50,
        "currency": "USD",
        "customs_clearance_days": 2,
    },
    "LAG-NAI": {
        "origin": "Lagos, Nigeria",
        "destination": "Nairobi, Kenya",
        "mode": "air",
        "distance_km": 4200,
        "transit_days": 3,
        "cost_usd_per_kg": 8.20,
        "currency": "USD",
        "customs_clearance_days": 3,
    },
    "LAG-JHB": {
        "origin": "Lagos, Nigeria",
        "destination": "Johannesburg, South Africa",
        "mode": "air",
        "distance_km": 5500,
        "transit_days": 4,
        "cost_usd_per_kg": 9.50,
        "currency": "USD",
        "customs_clearance_days": 3,
    },
    "LAG-LON": {
        "origin": "Lagos, Nigeria",
        "destination": "London, UK",
        "mode": "air",
        "distance_km": 6400,
        "transit_days": 3,
        "cost_usd_per_kg": 12.00,
        "currency": "USD",
        "customs_clearance_days": 2,
    },
    "LAG-SHA": {
        "origin": "Lagos, Nigeria",
        "destination": "Shanghai, China",
        "mode": "air",
        "distance_km": 12000,
        "transit_days": 5,
        "cost_usd_per_kg": 10.50,
        "currency": "USD",
        "customs_clearance_days": 4,
    },
    "LAG-ABV": {
        "origin": "Lagos, Nigeria",
        "destination": "Abuja, Nigeria",
        "mode": "road",
        "distance_km": 500,
        "transit_days": 2,
        "cost_usd_per_kg": 1.80,
        "currency": "USD",
        "customs_clearance_days": 0,
    },
    "LAG-PHC": {
        "origin": "Lagos, Nigeria",
        "destination": "Port Harcourt, Nigeria",
        "mode": "road",
        "distance_km": 620,
        "transit_days": 2,
        "cost_usd_per_kg": 2.00,
        "currency": "USD",
        "customs_clearance_days": 0,
    },
    "LAG-KAN": {
        "origin": "Lagos, Nigeria",
        "destination": "Kano, Nigeria",
        "mode": "road",
        "distance_km": 1100,
        "transit_days": 3,
        "cost_usd_per_kg": 2.50,
        "currency": "USD",
        "customs_clearance_days": 0,
    },
    "LAG-DUB": {
        "origin": "Lagos, Nigeria",
        "destination": "Dubai, UAE",
        "mode": "air",
        "distance_km": 7200,
        "transit_days": 3,
        "cost_usd_per_kg": 11.00,
        "currency": "USD",
        "customs_clearance_days": 2,
    },
}

SIMULATED_TRACKING: dict[str, dict[str, Any]] = {
    "DHL-NG-2026-001": {
        "tracking_code": "DHL-NG-2026-001",
        "origin": "Lagos, Nigeria",
        "destination": "Accra, Ghana",
        "status": "in_transit",
        "estimated_delivery": "2026-06-28",
        "carrier": "DHL",
        "events": [
            {"date": "2026-06-20", "location": "Lagos", "event": "Picked up by courier"},
            {"date": "2026-06-21", "location": "Lagos", "event": "Departed from sorting facility"},
            {"date": "2026-06-22", "location": "Cotonou, Benin", "event": "In transit — border crossing"},
        ],
    },
    "DHL-NG-2026-002": {
        "tracking_code": "DHL-NG-2026-002",
        "origin": "Lagos, Nigeria",
        "destination": "London, UK",
        "status": "delivered",
        "estimated_delivery": "2026-06-25",
        "carrier": "DHL",
        "events": [
            {"date": "2026-06-15", "location": "Lagos", "event": "Picked up by courier"},
            {"date": "2026-06-16", "location": "Lagos", "event": "Departed from sorting facility"},
            {"date": "2026-06-17", "location": "Accra, Ghana", "event": "Departed from regional hub"},
            {"date": "2026-06-18", "location": "London, UK", "event": "Arrived at customs"},
            {"date": "2026-06-19", "location": "London, UK", "event": "Customs cleared"},
            {"date": "2026-06-20", "location": "London, UK", "event": "Delivered"},
        ],
    },
    "GIG-NG-2026-001": {
        "tracking_code": "GIG-NG-2026-001",
        "origin": "Lagos, Nigeria",
        "destination": "Abuja, Nigeria",
        "status": "delivered",
        "estimated_delivery": "2026-06-24",
        "carrier": "GIG Logistics",
        "events": [
            {"date": "2026-06-19", "location": "Lagos", "event": "Picked up by courier"},
            {"date": "2026-06-20", "location": "Lagos", "event": "Departed from sorting facility"},
            {"date": "2026-06-22", "location": "Abuja", "event": "Arrived at destination hub"},
            {"date": "2026-06-23", "location": "Abuja", "event": "Out for delivery"},
            {"date": "2026-06-24", "location": "Abuja", "event": "Delivered"},
        ],
    },
    "GIG-NG-2026-002": {
        "tracking_code": "GIG-NG-2026-002",
        "origin": "Lagos, Nigeria",
        "destination": "Port Harcourt, Nigeria",
        "status": "in_transit",
        "estimated_delivery": "2026-06-26",
        "carrier": "GIG Logistics",
        "events": [
            {"date": "2026-06-21", "location": "Lagos", "event": "Picked up by courier"},
            {"date": "2026-06-22", "location": "Lagos", "event": "Departed from sorting facility"},
        ],
    },
    "GIG-NG-2026-003": {
        "tracking_code": "GIG-NG-2026-003",
        "origin": "Lagos, Nigeria",
        "destination": "Kano, Nigeria",
        "status": "pending",
        "estimated_delivery": "2026-06-27",
        "carrier": "GIG Logistics",
        "events": [
            {"date": "2026-06-22", "location": "Lagos", "event": "Label created"},
        ],
    },
}

ROUTE_KEYWORDS: dict[str, str] = {
    "accra": "LAG-ACC",
    "ghana": "LAG-ACC",
    "nairobi": "LAG-NAI",
    "kenya": "LAG-NAI",
    "johannesburg": "LAG-JHB",
    "south africa": "LAG-JHB",
    "london": "LAG-LON",
    "uk": "LAG-LON",
    "shanghai": "LAG-SHA",
    "china": "LAG-SHA",
    "abuja": "LAG-ABV",
    "port harcourt": "LAG-PHC",
    "kano": "LAG-KAN",
    "dubai": "LAG-DUB",
    "uae": "LAG-DUB",
}


class DHLAPITool(APITool):
    name = "dhl_api"
    description = "DHL shipping and logistics backend"

    def _is_configured(self) -> bool:
        return bool(settings.dhl_api_key)

    async def _dhl_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        import httpx
        headers = {
            "Authorization": f"Bearer {settings.dhl_api_key}",
            "Content-Type": "application/json",
        }
        url = f"https://api.dhl.com/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()


def _find_route(origin: str, destination: str) -> dict[str, Any] | None:
    orig_lower = origin.lower()
    dest_lower = destination.lower()

    for key, route in SIMULATED_ROUTES.items():
        if orig_lower in route["origin"].lower() and dest_lower in route["destination"].lower():
            return route

    dest_key = ROUTE_KEYWORDS.get(dest_lower)
    if dest_key and dest_key in SIMULATED_ROUTES:
        return SIMULATED_ROUTES[dest_key]

    return None


class EstimateShippingCostTool(BaseTool):
    name = "estimate_shipping_cost"
    description = "Estimate shipping cost based on weight, origin, and destination"

    async def execute(self, weight_kg: float, origin: str, destination: str,
                      mode: str | None = None) -> dict[str, Any]:
        route = _find_route(origin, destination)
        if not route:
            return {
                "status": "error",
                "message": f"No route found from '{origin}' to '{destination}'",
            }

        if mode and route["mode"] != mode:
            return {
                "status": "error",
                "message": f"No {mode} route available from '{origin}' to '{destination}'",
            }

        cost = round(weight_kg * route["cost_usd_per_kg"], 2)
        return {
            "status": "ok",
            "source": "simulated",
            "origin": route["origin"],
            "destination": route["destination"],
            "weight_kg": weight_kg,
            "mode": route["mode"],
            "distance_km": route["distance_km"],
            "estimated_cost_usd": cost,
            "cost_per_kg_usd": route["cost_usd_per_kg"],
            "transit_days": route["transit_days"],
            "customs_clearance_days": route["customs_clearance_days"],
            "currency": route["currency"],
        }


class ValidateDeliveryFeasibilityTool(BaseTool):
    name = "validate_delivery_feasibility"
    description = "Check if delivery is feasible from origin to destination within requested timeline"

    async def execute(self, origin: str, destination: str, requested_days: int,
                      weight_kg: float | None = None) -> dict[str, Any]:
        route = _find_route(origin, destination)
        if not route:
            return {
                "status": "error",
                "message": f"No route found from '{origin}' to '{destination}'",
            }

        total_days = route["transit_days"] + route["customs_clearance_days"]
        feasible = total_days <= requested_days

        return {
            "status": "ok",
            "source": "simulated",
            "origin": route["origin"],
            "destination": route["destination"],
            "mode": route["mode"],
            "distance_km": route["distance_km"],
            "transit_days": route["transit_days"],
            "customs_clearance_days": route["customs_clearance_days"],
            "total_estimated_days": total_days,
            "requested_days": requested_days,
            "feasible": feasible,
            "recommendation": "fastest" if feasible else "split_shipping",
        }


class CheckShippingRoutesTool(BaseTool):
    name = "check_shipping_routes"
    description = "Get available shipping routes, transit times, and modes between locations"

    async def execute(self, origin: str, destination: str) -> dict[str, Any]:
        route = _find_route(origin, destination)
        if not route:
            return {
                "status": "error",
                "message": f"No route found from '{origin}' to '{destination}'",
            }

        return {
            "status": "ok",
            "source": "simulated",
            "route_key": f"{route['origin']} → {route['destination']}",
            "origin": route["origin"],
            "destination": route["destination"],
            "mode": route["mode"],
            "distance_km": route["distance_km"],
            "transit_days": route["transit_days"],
            "customs_clearance_days": route["customs_clearance_days"],
            "cost_per_kg_usd": route["cost_usd_per_kg"],
            "currency": route["currency"],
            "available_alternatives": [],
        }


class TrackShipmentTool(BaseTool):
    name = "track_shipment"
    description = "Track a shipment by tracking code"

    async def execute(self, tracking_code: str) -> dict[str, Any]:
        result = SIMULATED_TRACKING.get(tracking_code)
        if not result:
            return {
                "status": "error",
                "message": f"Tracking code '{tracking_code}' not found",
            }

        return {
            "status": "ok",
            "source": "simulated",
            "tracking_code": result["tracking_code"],
            "carrier": result["carrier"],
            "origin": result["origin"],
            "destination": result["destination"],
            "current_status": result["status"],
            "estimated_delivery": result["estimated_delivery"],
            "events": result["events"],
        }
