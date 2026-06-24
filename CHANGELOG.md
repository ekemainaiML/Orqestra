# Changelog

## [0.2.0] — 2026-06-22

### Added
- Case search/filter API — search by text, status, workflow type; pagination via limit/offset
- Frontend dashboard search bar, status dropdown, workflow dropdown with debounced auto-fetch
- Monitoring & observability: `/health` with DB connectivity check, `GET /metrics` with request/error/duration counters, `RequestLoggingMiddleware` with duration tracking
- Admin workflow import/export endpoints
- Authentication pages (login, signup) with auth context provider
- Test coverage expanded from 143 → 168 tests: governance edge cases, API search/filter, challenge validator (12 new tests)
- Docker healthchecks (postgres, redis, backend) and restart policies
- Production-ready frontend Dockerfile with `NEXT_PUBLIC_API_URL` build arg
- `CORS_ORIGINS` env var for flexible CORS configuration
- `python-multipart` dependency for admin file upload support
- **New domain: Customer Onboarding** — `CustomerSuccessAgent`, `onboarding_service` tool (KYC, credit check, document verification), `customer_onboarding.yaml` workflow with 5 departments (Customer Success, Sales, Finance, Compliance, Ops Manager)
- **BaseTool adapter layer** — `BaseTool`/`APITool` base classes, `ToolRegistry`, `CircuitBreaker`, `RateLimiter` in `business_tools/base.py` and `business_tools/registry.py`
- Tool directory structure — `simulated/`, `crm/`, `erp/`, `payments/`, `logistics/` sub-packages
- Migrated all 10 simulated tools to `BaseTool` subclasses in `simulated/`

### Changed
- `definitions.py` — `TOOL_EXECUTOR` now sourced from `tool_registry.executor_map()`
- `qwen_client.py` — tool dispatch resolves through the registry
- `benchmark.py` — tool calls go through `tool_registry["tool_name"](**kwargs)`
- **HubSpot CRM integration** — 4 new tools (lookup_customer, get_customer_history, get_open_opportunities, get_customer_value) with real API path + simulated fallback
- `customer_db` agent tool now maps to HubSpot CRM tools instead of empty list
- `settings.py` — added `hubspot_api_key`, `hubspot_base_url`, `odoo_url`, `odoo_db`, `odoo_username`, `odoo_password`
- **Odoo ERP integration** — 5 new tools (create_rfq, create_purchase_order, check_budgets, validate_approvals, get_reorder_thresholds) with Odoo XML-RPC path + simulated fallback
- `erp_service` agent tool group maps to the 5 ERP tools
- **Paystack integration** — 4 new tools (verify_payment, check_transaction_history, assess_credit_risk, recommend_payment_terms) with simulated fallback
- `payment_service` added to Finance agent in all 3 workflows
- **DHL/GIG logistics integration** — 4 new tools (estimate_shipping_cost, validate_delivery_feasibility, check_shipping_routes, track_shipment) with 9 African/international routes + 5 sample tracking records
- `logistics_service` added to Logistics agent in order_fulfillment.yaml (replaced supplier_db)
- **Multi-tenancy** — Tenant model, TenantMixin on all 8 data tables, do_orm_execute auto-filter, before_flush auto-set on INSERT, TenantMiddleware (JWT + header), token now includes tenant_id, POST/GET /auth/tenants endpoints, default tenant seeded on startup
- **Notification system** — EmailSender (SMTP via aiosmtplib), SlackNotifier (webhook), NotificationService integrated into event publisher, triggers on escalated/completed/rejected/failed/approval_pending events
- **Qwen client hardening** — Added retry logic (3 attempts, exponential backoff 0/10/30s) to `assess_with_tools` and `assess_raw`; added `aiosmtplib` dependency (government_procurement, order_fulfillment, customer_onboarding)

### Fixed
- Frontend SSE timeout: `RUN_TIMEOUT_MS` increased from 120s → 300s
- Qwen OpenAI client: 30s HTTP timeout to prevent indefinite hangs
- Session propagation: session passed through `assess_agent` → `retrieve_for_agent`
- React duplicate-key bugs in `DepartmentAssessments` and admin workflows page
- Backend duplicate workflow IDs in `list_all_configs` (custom overrides built-in)
- `UnboundLocalError` for `rec_text` in adjudicator budget-compliance check
- Dashboard dropdown height (`h-8` → `h-10`) so default options are visible
- ESLint `set-state-in-effect` errors (5 files) and unused imports (7 files)
- Ruff E501 line-too-long errors (18 files) and import sorting (7 files)
- TypeScript build error in benchmark page (`WorkflowSummary` import)

### Changed
- Backend version bumped to 0.2.0 (from 0.1.0)
- Frontend version bumped to 0.2.0 (from 0.1.0)

## [0.1.0] — 2026-06-?? (Initial Release)

### Added
- Backend scaffold: FastAPI, SQLAlchemy async models, Alembic, asyncpg, Redis
- Multi-agent deliberation engine with 6 agent types
- Qwen AI client (OpenAI-compatible SDK, tiered model routing)
- Business simulation tools (Inventory, Pricing, SupplierDB, Policy Engine)
- Memory engine with 3-layer retrieval (entity, department, organizational)
- Governance engine (brief generator, approval handler, iteration manager)
- Challenge validator, scoring engine, adjudicator, state machine
- Event store with SSE streaming
- REST API (case CRUD, demo launch, governance, SSE, benchmark, dashboard)
- Frontend: Next.js with 8 pages, 10 components, SSE client, type definitions
- Replay mode (event replay endpoint, frontend replay page)
- Docker Compose deployment with postgres, redis, backend, frontend
- CI pipeline with lint, type-check, test, and Docker build
- Devpost submission assets
