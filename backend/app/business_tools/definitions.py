from typing import Any

from app.business_tools import inventory_service, policy_engine, pricing_engine, supplier_db

QWEN_TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "calculate_price": {
        "type": "function",
        "function": {
            "name": "calculate_price",
            "description": (
                "Calculate unit price, subtotal, margin and"
                " applicable discounts based on quantity and client type"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {"type": "integer", "description": "Number of units ordered"},
                    "is_preferred": {"type": "boolean", "description": "Whether the client is a preferred client"},
                    "is_government": {"type": "boolean", "description": "Whether the client is a government entity"},
                },
                "required": ["quantity"],
            },
        },
    },
    "get_exchange_rate": {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get simulated exchange rate between two currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {"type": "string", "description": "Base currency code (e.g. USD)", "default": "USD"},
                    "target": {"type": "string", "description": "Target currency code (e.g. NGN)", "default": "NGN"},
                },
                "required": [],
            },
        },
    },
    "check_availability": {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check current stock availability for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product identifier (e.g. solar_street_light_60w)"},
                    "quantity": {"type": "integer", "description": "Requested quantity"},
                },
                "required": ["product", "quantity"],
            },
        },
    },
    "get_product_specs": {
        "type": "function",
        "function": {
            "name": "get_product_specs",
            "description": "Get technical specifications for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product identifier (e.g. solar_street_light_60w)"},
                },
                "required": ["product"],
            },
        },
    },
    "find_suppliers": {
        "type": "function",
        "function": {
            "name": "find_suppliers",
            "description": "Find suppliers matching region and minimum reliability criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Filter by region (e.g. Asia, Africa)",
                        "default": None,
                    },
                    "min_reliability": {
                        "type": "number",
                        "description": "Minimum reliability score (0.0 to 1.0)",
                        "default": 0.0,
                    },
                },
                "required": [],
            },
        },
    },
    "get_supplier": {
        "type": "function",
        "function": {
            "name": "get_supplier",
            "description": "Get detailed information about a specific supplier by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "supplier_id": {
                        "type": "string",
                        "description": "Supplier UUID (e.g. b2c3d4e5-0001-4000-8000-000000000001)",
                    },
                },
                "required": ["supplier_id"],
            },
        },
    },
    "check_policy": {
        "type": "function",
        "function": {
            "name": "check_policy",
            "description": "Check a specific policy against a business context to determine compliance",
            "parameters": {
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": (
                            "Policy identifier (e.g. minimum_margin,"
                            " new_client_deposit, government_payment_terms,"
                            " preferred_supplier, customs_buffer)"
                        ),
                    },
                    "context": {
                        "type": "object",
                        "description": (
                            'Business context to evaluate against'
                            ' (e.g. {"margin_pct": 18.5, "is_new_client": false})'
                        ),
                    },
                },
                "required": ["policy_id", "context"],
            },
        },
    },
    "get_all_policies": {
        "type": "function",
        "function": {
            "name": "get_all_policies",
            "description": "Get all available business policies with their descriptions and types",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
}

TOOL_EXECUTOR: dict[str, Any] = {
    "calculate_price": pricing_engine.calculate_price,
    "get_exchange_rate": pricing_engine.get_exchange_rate,
    "check_availability": inventory_service.check_availability,
    "get_product_specs": inventory_service.get_product_specs,
    "find_suppliers": supplier_db.find_suppliers,
    "get_supplier": supplier_db.get_supplier,
    "check_policy": policy_engine.check_policy,
    "get_all_policies": policy_engine.get_all_policies,
}


def get_tool_definitions(tool_names: list[str]) -> list[dict[str, Any]]:
    return [QWEN_TOOL_DEFINITIONS[name] for name in tool_names if name in QWEN_TOOL_DEFINITIONS]


def get_tool_names_for_agent(agent_tools: list[str]) -> list[str]:
    mapping = {
        "pricing_engine": ["calculate_price", "get_exchange_rate"],
        "inventory_service": ["check_availability", "get_product_specs"],
        "supplier_db": ["find_suppliers", "get_supplier"],
        "policy_engine": ["check_policy", "get_all_policies"],
        "customer_db": [],
    }
    names = []
    for t in agent_tools:
        names.extend(mapping.get(t, []))
    return names
