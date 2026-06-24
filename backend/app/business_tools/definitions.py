from typing import Any

from app.business_tools import tool_registry

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
    "check_kyc": {
        "type": "function",
        "function": {
            "name": "check_kyc",
            "description": "Check KYC status and customer segment information",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "check_credit": {
        "type": "function",
        "function": {
            "name": "check_credit",
            "description": "Check customer credit score and determine if deposit is required",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "verify_documents": {
        "type": "function",
        "function": {
            "name": "verify_documents",
            "description": "Verify customer documentation completeness for onboarding",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "lookup_customer": {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up customer details by ID or email via CRM",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer email address",
                    },
                },
            },
        },
    },
    "get_customer_history": {
        "type": "function",
        "function": {
            "name": "get_customer_history",
            "description": "Get customer payment and order history",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "get_open_opportunities": {
        "type": "function",
        "function": {
            "name": "get_open_opportunities",
            "description": "Get open sales opportunities and pipeline value",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "get_customer_value": {
        "type": "function",
        "function": {
            "name": "get_customer_value",
            "description": "Get customer lifetime value and segment information",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "create_rfq": {
        "type": "function",
        "function": {
            "name": "create_rfq",
            "description": "Create a request for quotation (RFQ) for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product identifier"},
                    "quantity": {"type": "integer", "description": "Requested quantity"},
                    "supplier_id": {"type": "string", "description": "Preferred supplier UUID (optional)"},
                    "notes": {"type": "string", "description": "Additional notes for the RFQ"},
                },
                "required": ["product", "quantity"],
            },
        },
    },
    "create_purchase_order": {
        "type": "function",
        "function": {
            "name": "create_purchase_order",
            "description": "Create a purchase order for products from a supplier",
            "parameters": {
                "type": "object",
                "properties": {
                    "supplier": {"type": "string", "description": "Supplier name or ID"},
                    "product": {"type": "string", "description": "Product identifier"},
                    "quantity": {"type": "integer", "description": "Order quantity"},
                    "unit_price": {"type": "number", "description": "Agreed unit price"},
                    "notes": {"type": "string", "description": "Purchase order notes"},
                },
                "required": ["supplier", "product", "quantity", "unit_price"],
            },
        },
    },
    "check_budgets": {
        "type": "function",
        "function": {
            "name": "check_budgets",
            "description": "Check budget availability for a product or department",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product identifier (optional)"},
                    "department": {"type": "string", "description": "Department name (optional)"},
                },
            },
        },
    },
    "validate_approvals": {
        "type": "function",
        "function": {
            "name": "validate_approvals",
            "description": "Check approval status for purchase orders or budget items",
            "parameters": {
                "type": "object",
                "properties": {
                    "po_id": {"type": "string", "description": "Purchase order ID to check (optional)"},
                },
            },
        },
    },
    "get_reorder_thresholds": {
        "type": "function",
        "function": {
            "name": "get_reorder_thresholds",
            "description": "Get reorder thresholds and stock level recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product identifier (optional)"},
                },
            },
        },
    },
    "verify_payment": {
        "type": "function",
        "function": {
            "name": "verify_payment",
            "description": "Verify a payment transaction by reference code via Paystack",
            "parameters": {
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "Payment reference code (e.g. TXN-001)",
                    },
                },
                "required": ["reference"],
            },
        },
    },
    "check_transaction_history": {
        "type": "function",
        "function": {
            "name": "check_transaction_history",
            "description": "Get transaction history and payment patterns for a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "assess_credit_risk": {
        "type": "function",
        "function": {
            "name": "assess_credit_risk",
            "description": "Assess credit risk for a customer based on payment history",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    "estimate_shipping_cost": {
        "type": "function",
        "function": {
            "name": "estimate_shipping_cost",
            "description": "Estimate shipping cost based on weight, origin, and destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Weight of shipment in kilograms"},
                    "origin": {"type": "string", "description": "Origin city or country (e.g. Lagos)"},
                    "destination": {"type": "string", "description": "Destination city or country (e.g. Accra)"},
                    "mode": {"type": "string", "description": "Shipping mode: road or air (optional)"},
                },
                "required": ["weight_kg", "origin", "destination"],
            },
        },
    },
    "validate_delivery_feasibility": {
        "type": "function",
        "function": {
            "name": "validate_delivery_feasibility",
            "description": "Check if delivery is feasible from origin to destination within requested timeline",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin city or country"},
                    "destination": {"type": "string", "description": "Destination city or country"},
                    "requested_days": {"type": "integer", "description": "Requested delivery timeline in days"},
                    "weight_kg": {"type": "number", "description": "Weight of shipment in kilograms (optional)"},
                },
                "required": ["origin", "destination", "requested_days"],
            },
        },
    },
    "check_shipping_routes": {
        "type": "function",
        "function": {
            "name": "check_shipping_routes",
            "description": "Get available shipping routes, transit times, and modes between locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin city or country"},
                    "destination": {"type": "string", "description": "Destination city or country"},
                },
                "required": ["origin", "destination"],
            },
        },
    },
    "track_shipment": {
        "type": "function",
        "function": {
            "name": "track_shipment",
            "description": "Track a shipment by tracking code",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_code": {
                        "type": "string",
                        "description": "Tracking code (e.g. DHL-NG-2026-001 or GIG-NG-2026-001)",
                    },
                },
                "required": ["tracking_code"],
            },
        },
    },
    "recommend_payment_terms": {
        "type": "function",
        "function": {
            "name": "recommend_payment_terms",
            "description": "Recommend payment terms based on customer history and risk profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer UUID",
                    },
                    "requested_terms": {
                        "type": "string",
                        "description": "Customer's requested terms (optional)",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Order amount in USD (optional)",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
}

TOOL_EXECUTOR: dict[str, Any] = tool_registry.executor_map()


def get_tool_definitions(tool_names: list[str]) -> list[dict[str, Any]]:
    return [QWEN_TOOL_DEFINITIONS[name] for name in tool_names if name in QWEN_TOOL_DEFINITIONS]


def get_tool_names_for_agent(agent_tools: list[str]) -> list[str]:
    mapping = {
        "pricing_engine": ["calculate_price", "get_exchange_rate"],
        "inventory_service": ["check_availability", "get_product_specs"],
        "supplier_db": ["find_suppliers", "get_supplier"],
        "policy_engine": ["check_policy", "get_all_policies"],
        "customer_db": ["lookup_customer", "get_customer_history", "get_open_opportunities", "get_customer_value"],
        "onboarding_service": ["check_kyc", "check_credit", "verify_documents"],
    "erp_service": [
        "create_rfq", "create_purchase_order", "check_budgets",
        "validate_approvals", "get_reorder_thresholds",
    ],
    "payment_service": [
        "verify_payment", "check_transaction_history",
        "assess_credit_risk", "recommend_payment_terms",
    ],
    "logistics_service": [
        "estimate_shipping_cost", "validate_delivery_feasibility",
        "check_shipping_routes", "track_shipment",
    ],
    }
    names = []
    for t in agent_tools:
        names.extend(mapping.get(t, []))
    return names
