from typing import Any

from app.business_tools.base import BaseTool
from app.services.settings import settings

SIMULATED_BUDGETS: dict[str, dict[str, Any]] = {
    "solar_street_light_60w": {
        "product": "solar_street_light_60w",
        "department": "infrastructure",
        "allocated": 500000.00,
        "spent": 285000.00,
        "remaining": 215000.00,
        "currency": "USD",
    },
    "solar_street_light_100w": {
        "product": "solar_street_light_100w",
        "department": "infrastructure",
        "allocated": 750000.00,
        "spent": 410000.00,
        "remaining": 340000.00,
        "currency": "USD",
    },
    "solar_panel_300w": {
        "product": "solar_panel_300w",
        "department": "energy",
        "allocated": 300000.00,
        "spent": 120000.00,
        "remaining": 180000.00,
        "currency": "USD",
    },
}

SIMULATED_PURCHASE_ORDERS: list[dict[str, Any]] = [
    {"id": "PO-2026-001", "supplier": "SolarTech Manufacturing", "product": "solar_street_light_60w",
     "quantity": 150, "total": 27000.00, "status": "approved", "created": "2026-05-12"},
    {"id": "PO-2026-002", "supplier": "AfriEnergy Components", "product": "solar_street_light_100w",
     "quantity": 80, "total": 16800.00, "status": "pending_approval", "created": "2026-06-01"},
    {"id": "PO-2026-003", "supplier": "BrightPath Solar Co.", "product": "solar_panel_300w",
     "quantity": 200, "total": 31000.00, "status": "draft", "created": "2026-06-15"},
]

SIMULATED_REORDER_THRESHOLDS: dict[str, dict[str, Any]] = {
    "solar_street_light_60w": {"product": "solar_street_light_60w",
                                "current_stock": 200, "reorder_at": 50, "reorder_qty": 100,
                                "lead_time_days": 10, "auto_approve": True},
    "solar_street_light_100w": {"product": "solar_street_light_100w",
                                "current_stock": 150, "reorder_at": 30, "reorder_qty": 75,
                                "lead_time_days": 14, "auto_approve": False},
    "solar_panel_300w": {"product": "solar_panel_300w",
                         "current_stock": 300, "reorder_at": 80, "reorder_qty": 150,
                         "lead_time_days": 7, "auto_approve": True},
    "battery_12v_100ah": {"product": "battery_12v_100ah",
                          "current_stock": 250, "reorder_at": 60, "reorder_qty": 120,
                          "lead_time_days": 10, "auto_approve": True},
    "charge_controller_30a": {"product": "charge_controller_30a",
                              "current_stock": 180, "reorder_at": 40, "reorder_qty": 80,
                              "lead_time_days": 7, "auto_approve": False},
}


class OdooERPTool:
    """ERP backend for inventory, procurement, and finance data via Odoo (utility, not a registered tool)"""

    def _is_configured(self) -> bool:
        return bool(settings.odoo_url and settings.odoo_db and settings.odoo_username and settings.odoo_password)

    async def _authenticate(self) -> int | None:
        import httpx
        url = f"{settings.odoo_url}/jsonrpc"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "login",
                    "args": [settings.odoo_db, settings.odoo_username, settings.odoo_password],
                },
                "id": 1,
            })
            data = resp.json()
            uid = data.get("result")
            return uid if isinstance(uid, int) else None

    async def _odoo_execute(self, method: str, model: str, args: list[Any],
                             kwargs: dict[str, Any] | None = None) -> Any:
        uid = await self._authenticate()
        if not uid:
            raise ConnectionError("Odoo authentication failed")
        import httpx
        url = f"{settings.odoo_url}/jsonrpc"
        exec_args = [settings.odoo_db, uid, settings.odoo_password, model, method, args]
        if kwargs:
            exec_args.append(kwargs)
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": exec_args,
            },
            "id": 1,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            if "result" in data:
                return data["result"]
            return data

    async def _odoo_search_read(self, model: str, fields: list[str],
                                 domain: list[Any] | None = None) -> list[dict[str, Any]]:
        try:
            return await self._odoo_execute("search_read", model, [domain or [], fields]) or []
        except Exception:
            return []

    async def _odoo_create(self, model: str, values: dict[str, Any]) -> int | None:
        try:
            result = await self._odoo_execute("create", model, [values])
            return int(result) if result else None
        except Exception:
            return None


class CreateRfqTool(BaseTool):
    name = "create_rfq"
    description = "Create a request for quotation (RFQ) in the ERP"

    async def execute(  # type: ignore[override]
            self, product: str, quantity: int, supplier_id: str | None = None,
            notes: str | None = None) -> dict[str, Any]:
        odoo = OdooERPTool()
        if odoo._is_configured():
            vendor_id = int(supplier_id) if supplier_id and supplier_id.isdigit() else None
            vals: dict[str, Any] = {
                "line_ids": [(0, 0, {"product_id": int(product) if product.isdigit() else product,
                                     "product_qty": quantity})],
            }
            if vendor_id:
                vals["vendor_id"] = vendor_id
            rfq_id = await odoo._odoo_create("purchase.requisition", vals)
            if rfq_id:
                return {
                    "status": "ok",
                    "source": "odoo",
                    "rfq_id": f"RFQ-{rfq_id:05d}",
                    "product": product,
                    "quantity": quantity,
                    "supplier_id": supplier_id or "open",
                    "notes": notes or "",
                    "rfq_status": "draft",
                }
        return {
            "status": "ok",
            "source": "simulated",
            "rfq_id": f"RFQ-{hash(product + str(quantity)) % 100000:05d}",
            "product": product,
            "quantity": quantity,
            "supplier_id": supplier_id or "open",
            "notes": notes or "",
            "created": "2026-06-22",
            "rfq_status": "pending_quotes",
        }


class CreatePurchaseOrderTool(BaseTool):
    name = "create_purchase_order"
    description = "Create a purchase order in the ERP"

    async def execute(  # type: ignore[override]
            self, supplier: str, product: str, quantity: int,
            unit_price: float, notes: str | None = None) -> dict[str, Any]:
        odoo = OdooERPTool()
        if odoo._is_configured():
            vals: dict[str, Any] = {
                "partner_id": int(supplier) if supplier.isdigit() else supplier,
                "order_line": [(0, 0, {
                    "product_id": int(product) if product.isdigit() else product,
                    "product_qty": quantity,
                    "price_unit": unit_price,
                })],
            }
            po_id = await odoo._odoo_create("purchase.order", vals)
            if po_id:
                total = round(quantity * unit_price, 2)
                return {
                    "status": "ok",
                    "source": "odoo",
                    "po_id": f"PO-{po_id:05d}",
                    "supplier": supplier,
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": total,
                    "notes": notes or "",
                    "order_status": "draft",
                }
        total = round(quantity * unit_price, 2)
        sim_po_id = f"PO-2026-{len(SIMULATED_PURCHASE_ORDERS) + 1:04d}"
        return {
            "status": "ok",
            "source": "simulated",
            "po_id": sim_po_id,
            "supplier": supplier,
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": total,
            "notes": notes or "",
            "created": "2026-06-22",
            "order_status": "draft",
        }


class CheckBudgetsTool(BaseTool):
    name = "check_budgets"
    description = "Check budget availability for a product, project, or department"

    async def execute(  # type: ignore[override]
            self, product: str | None = None,
            department: str | None = None) -> dict[str, Any]:
        odoo = OdooERPTool()
        if odoo._is_configured():
            domain: list[Any] = []
            if department:
                domain.append(("department", "=", department))
            records = await odoo._odoo_search_read(
                "account.budget",
                ["name", "date_from", "date_to", "planned_amount", "practical_amount"],
                domain,
            )
            if records:
                budgets = []
                for r in records:
                    allocated = float(r.get("planned_amount", 0))
                    spent = float(r.get("practical_amount", 0))
                    budgets.append({
                        "product": r.get("name", "unknown"),
                        "department": department or "general",
                        "allocated": allocated,
                        "spent": spent,
                        "remaining": allocated - spent,
                        "currency": "USD",
                    })
                total_remaining = sum(b["remaining"] for b in budgets)
                return {
                    "status": "ok",
                    "source": "odoo",
                    "budgets": budgets,
                    "total_remaining": total_remaining,
                }
        if product and product in SIMULATED_BUDGETS:
            b = SIMULATED_BUDGETS[product]
            return {
                "status": "ok",
                "source": "simulated",
                "budgets": [b],
                "total_remaining": b["remaining"],
            }
        budgets = list(SIMULATED_BUDGETS.values())
        if department:
            budgets = [b for b in budgets if b["department"] == department]
        total_remaining = sum(b["remaining"] for b in budgets)
        return {
            "status": "ok",
            "source": "simulated",
            "budgets": budgets,
            "total_remaining": total_remaining,
        }


class ValidateApprovalsTool(BaseTool):
    name = "validate_approvals"
    description = "Check approval status and requirements for purchase orders or budget items"

    async def execute(self, po_id: str | None = None) -> dict[str, Any]:  # type: ignore[override]
        odoo = OdooERPTool()
        if odoo._is_configured():
            if po_id:
                numeric_id = po_id.replace("PO-", "")
                if numeric_id.isdigit():
                    records = await odoo._odoo_search_read(
                        "purchase.order",
                        ["name", "state", "partner_id", "amount_total"],
                        [("id", "=", int(numeric_id))],
                    )
                    if records:
                        r = records[0]
                        state = r.get("state", "draft")
                        total = float(r.get("amount_total", 0))
                        partner = r.get("partner_id", "")
                        partner_name = (
                            partner[1] if isinstance(partner, (list, tuple))
                            and len(partner) > 1 else str(partner)
                        )
                        return {
                            "status": "ok",
                            "source": "odoo",
                            "po_id": po_id,
                            "current_status": state,
                            "requires_approval": state == "draft",
                            "approval_chain": ["manager", "finance", "director"] if total > 25000 else ["manager"],
                        }
                    return {"status": "error", "message": f"Purchase order not found: {po_id}"}
            pending = await odoo._odoo_search_read(
                "purchase.order",
                ["name", "state", "partner_id", "amount_total"],
                [("state", "!=", "purchase")],
            )
            if pending:
                items = []
                for r in pending:
                    partner = r.get("partner_id", "")
                    partner_name = (
                        partner[1] if isinstance(partner, (list, tuple))
                        and len(partner) > 1 else str(partner)
                    )
                    items.append({
                        "id": r.get("name", f"PO-{r['id']:05d}"),
                        "supplier": partner_name,
                        "product": "various",
                        "total": float(r.get("amount_total", 0)),
                        "status": r.get("state", "draft"),
                    })
                return {
                    "status": "ok",
                    "source": "odoo",
                    "pending_approvals": len(items),
                    "items": items,
                }
        if po_id:
            for po in SIMULATED_PURCHASE_ORDERS:
                if po["id"] == po_id:
                    return {
                        "status": "ok",
                        "source": "simulated",
                        "po_id": po_id,
                        "current_status": po["status"],
                        "requires_approval": po["status"] == "draft",
                        "approval_chain": ["manager", "finance", "director"] if po["total"] > 25000 else ["manager"],
                    }
            return {"status": "error", "message": f"Purchase order not found: {po_id}"}
        pending = [po for po in SIMULATED_PURCHASE_ORDERS if po["status"] != "approved"]
        return {
            "status": "ok",
            "source": "simulated",
            "pending_approvals": len(pending),
            "items": pending,
        }


class GetReorderThresholdsTool(BaseTool):
    name = "get_reorder_thresholds"
    description = "Get reorder thresholds and stock level recommendations for inventory"

    async def execute(self, product: str | None = None) -> dict[str, Any]:  # type: ignore[override]
        odoo = OdooERPTool()
        if odoo._is_configured():
            domain: list[Any] = []
            if product:
                domain.append(("default_code", "=", product))
            products = await odoo._odoo_search_read(
                "product.product",
                ["id", "default_code", "name", "type", "qty_available"],
                domain,
            )
            if products:
                items = []
                for p in products:
                    qty = float(p.get("qty_available", 0))
                    reorder_at = max(10, int(qty * 0.25))
                    items.append({
                        "product": p.get("default_code", p["id"]),
                        "current_stock": qty,
                        "reorder_at": reorder_at,
                        "reorder_qty": reorder_at * 2,
                        "lead_time_days": 7,
                        "auto_approve": qty > 50,
                    })
                needs_reorder = [i["product"] for i in items if i["current_stock"] <= i["reorder_at"]]
                return {
                    "status": "ok",
                    "source": "odoo",
                    "items": items,
                    "needs_reorder": needs_reorder,
                }
        if product and product in SIMULATED_REORDER_THRESHOLDS:
            item = SIMULATED_REORDER_THRESHOLDS[product]
            needs_reorder = item["current_stock"] <= item["reorder_at"]
            return {
                "status": "ok",
                "source": "simulated",
                "items": [item],
                "needs_reorder": [product] if needs_reorder else [],
            }
        items = list(SIMULATED_REORDER_THRESHOLDS.values())
        needs_reorder = [k for k, v in SIMULATED_REORDER_THRESHOLDS.items() if v["current_stock"] <= v["reorder_at"]]
        return {
            "status": "ok",
            "source": "simulated",
            "items": items,
            "needs_reorder": needs_reorder,
        }
