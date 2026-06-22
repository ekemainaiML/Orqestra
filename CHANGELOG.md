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
