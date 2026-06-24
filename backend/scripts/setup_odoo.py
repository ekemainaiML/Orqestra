"""Setup Odoo database, install modules, and create seed data for Orqestra.

Usage:
    python scripts/setup_odoo.py

Requires Odoo 18 running at http://localhost:8069.
Run `docker compose -f docker-compose.odoo.yml up -d` first.
"""

import json
import sys
import time
import urllib.request
import xmlrpc.client
from urllib.error import HTTPError

ODOO_URL = "http://localhost:8069"
DB_NAME = "orqestra_odoo"
MASTER_PASSWORD = "admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "StrongPassword123"


def _jsonrpc_call(method, params, url=f"{ODOO_URL}/jsonrpc"):
    payload = json.dumps({"jsonrpc": "2.0", "method": "call",
                          "params": params, "id": 1}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        return {"error": str(e), "body": e.read().decode()}


def create_database():
    result = _jsonrpc_call("call", {
        "service": "db",
        "method": "create_database",
        "args": [MASTER_PASSWORD, DB_NAME, True, "en_US", ADMIN_PASSWORD, ADMIN_EMAIL],
    })
    if result.get("result") is True:
        print(f"  Database '{DB_NAME}' created.")
        return True
    error = result.get("error", {})
    msg = error.get("data", {}).get("message", "") if isinstance(error, dict) else ""
    if "already exists" in msg:
        print(f"  Database '{DB_NAME}' already exists.")
        return True
    print(f"  Unexpected: {result}")
    return False


def get_uid():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    for i in range(30):
        try:
            uid = common.authenticate(DB_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, {})
            if uid:
                print(f"  Authenticated as uid {uid}")
                return uid
        except Exception:
            pass
        time.sleep(2)
    print("  Authentication failed after 60s.")
    sys.exit(1)


def install_modules(uid, module_names):
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    for mod in module_names:
        mod_ids = models.execute_kw(
            DB_NAME, uid, ADMIN_PASSWORD,
            "ir.module.module", "search",
            [[("name", "=", mod), ("state", "=", "uninstalled")]],
        )
        if mod_ids:
            print(f"  Installing '{mod}'...")
            models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                              "ir.module.module", "button_immediate_install", [mod_ids])
            print(f"    '{mod}' installed.")
        else:
            print(f"  '{mod}' already installed.")


def create_suppliers(uid):
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    suppliers = [
        {"name": "SolarTech Nigeria", "supplier_rank": 1, "company_type": "company",
         "email": "info@solartech.ng"},
        {"name": "Green Energy Solutions", "supplier_rank": 1, "company_type": "company",
         "email": "sales@greenenergy.ke"},
        {"name": "BrightLight Industries", "supplier_rank": 1, "company_type": "company",
         "email": "orders@brightlight.co.za"},
    ]
    ids = []
    for s in suppliers:
        existing = models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                                     "res.partner", "search", [[("name", "=", s["name"])]])
        if existing:
            print(f"  Supplier '{s['name']}' exists (id {existing[0]}).")
            ids.append(existing[0])
        else:
            pid = models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                                    "res.partner", "create", [s])
            print(f"  Created supplier '{s['name']}' (id {pid}).")
            ids.append(pid)
    return ids


def create_products(uid):
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    products = [
        {"name": "100W Solar Street Light", "default_code": "solar_street_light_100w",
         "type": "consu", "list_price": 250.0, "standard_price": 180.0,
         "uom_id": 1, "uom_po_id": 1},
        {"name": "200W Solar Street Light", "default_code": "solar_street_light_200w",
         "type": "consu", "list_price": 420.0, "standard_price": 310.0,
         "uom_id": 1, "uom_po_id": 1},
        {"name": "Solar Flood Light", "default_code": "solar_flood_light",
         "type": "consu", "list_price": 180.0, "standard_price": 120.0,
         "uom_id": 1, "uom_po_id": 1},
    ]
    ids = []
    for p in products:
        existing = models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                                     "product.product", "search",
                                     [[("default_code", "=", p["default_code"])]])
        if existing:
            print(f"  Product '{p['name']}' exists (id {existing[0]}).")
            ids.append(existing[0])
        else:
            tmpl_id = models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                                        "product.template", "create", [p])
            prod_ids = models.execute_kw(DB_NAME, uid, ADMIN_PASSWORD,
                                         "product.product", "search",
                                         [[("product_tmpl_id", "=", tmpl_id)]])
            pid = prod_ids[0] if prod_ids else None
            print(f"  Created '{p['name']}' (product id {pid}).")
            ids.append(pid)
    return ids


def main():
    print("=== Odoo Setup for Orqestra ===\n")

    print("--- Creating Database ---")
    print(f"Connecting to Odoo at {ODOO_URL}...")
    if not create_database():
        print("Database creation failed.")
        sys.exit(1)

    print("\n--- Authenticating ---")
    uid = get_uid()

    print("\n--- Installing Modules ---")
    install_modules(uid, ["purchase", "sale", "stock", "account", "purchase_requisition"])

    print("\n--- Creating Suppliers ---")
    supplier_ids = create_suppliers(uid)

    print("\n--- Creating Products ---")
    product_ids = create_products(uid)

    print(f"\n=== Setup Complete ===")
    print(f"Login:  {ODOO_URL}/web")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"\nSuppliers: {len(supplier_ids)} → IDs: {supplier_ids}")
    print(f"Products:  {len(product_ids)} → IDs: {product_ids}")


if __name__ == "__main__":
    main()
