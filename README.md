# Orqestra

**Autonomous AI Workforce for Business Operations**

Orqestra is an AI-powered platform where specialized agents — Sales, Finance, Inventory, Procurement, Logistics, and an Operations Manager — collaborate as digital departments to automate customer order fulfillment. It uses a 4-stage governance protocol (Independent Assessment → Challenge → Consensus → Adjudication) with human-in-the-loop approval, organizational memory, and full audit trails.

---

## Overview

| Department | Agent | Model | Role |
|---|---|---|---|---|
| Sales | Sales Agent | qwen3.6-flash | Interpret customer intent, generate quotations |
| Finance | Finance Agent | qwen3.6-flash | Evaluate profitability, financial risk, policy compliance |
| Inventory | Inventory Agent | qwen3.6-flash | Check stock availability, assess make-vs-buy |
| Procurement | Procurement Agent | qwen3.6-flash | Identify suppliers, evaluate sourcing options |
| Logistics | Logistics Agent | qwen3.6-flash | Validate delivery feasibility, shipping risk |
| Executive | Operations Manager | qwen-max | Synthesize inputs, adjudicate conflicts, final decision |

**Demo workflow:** Customer orders 500 solar-powered street lights with 14-day delivery. Agents deliberate, the Operations Manager adjudicates, and a human operator approves, rejects, or modifies the decision.

> **New to Orqestra?** Start with the [User Guide](docs/user-guide.md) for a step-by-step walkthrough of every feature.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)              │
│  Dashboard │ Demo Library │ Case Detail │ Benchmark  │
│  Audit Trail │ Replay │ New Case │ Theme Toggle      │
└────────────────────────┬─────────────────────────────┘
                         │ HTTP / SSE
┌────────────────────────▼─────────────────────────────┐
│                  Backend (FastAPI)                    │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Governance│ │Delibera- │ │  Memory  │ │ Events  │ │
│  │  Engine  │ │tion Eng. │ │  Engine  │ │  Layer  │ │
│  │ Brief/   │ │ 5 agents │ │ 3-tier   │ │ Pub/Sub │ │
│  │ Approve/ │ │ Scoring  │ │ retrieval │ │  SSE    │ │
│  │ Reject   │ │State Mach│ │ promotion│ │Storage  │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                       │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐│
│  │ Business    │ │  Agent       │ │  Qwen Cloud    ││
│  │ Tools       │ │  Registry    │ │  Client        ││
│  │ (pricing/   │ │  (6 agents)  │ │  (OpenAI SDK)  ││
│  │ inventory/  │ │              │ │                ││
│  │ supplier/   │ │              │ │                ││
│  │ policy)     │ │              │ │                ││
│  └─────────────┘ └──────────────┘ └────────────────┘│
└────────────────────────┬─────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │  PostgreSQL  │ Redis │
              └──────────────────────┘
```

**Core pipeline:** Customer Request → Memory Retrieval → Independent Assessment (5 agents in parallel) → Challenge Round → Consensus Scoring → Adjudication (Ops Manager) → Approval Pending → Human Decision

**Deliberation quality metrics:** 215 automated tests (unit + integration + E2E), structured monitoring with request-level metrics, DB health checks, and duration tracking built in.

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local backend)
- Node.js 20+ (for local frontend)

### Docker (recommended)

```bash
# Clone and start all services
git clone <repo-url>
cd orqestra

# Set your Qwen Cloud API key
export DASHSCOPE_API_KEY=sk-...

# Start everything
docker compose up --build
```

The app will be available at `http://localhost:3000`. The first startup runs database migrations and seeds demo data automatically.

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -e .

# Ensure PostgreSQL (port 5432 or match DATABASE_URL) and Redis are running, then:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> The docker-compose exposes PostgreSQL on port **5433** to avoid conflicts. For local dev, set `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/orqestra` or use a local PostgreSQL on the default port 5432.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Environment variables** (see `backend/.env.example`):
| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://postgres:postgres@localhost:5432/orqestra` | PostgreSQL connection string |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection string |
| `DASHSCOPE_API_KEY` | Yes | — | Alibaba Cloud Qwen API key (get from [DashScope Console](https://dashscope.console.aliyun.com/)) |
| `QWEN_MODEL_OPERATIONAL` | No | `qwen3.6-flash` | Model for operational agents |
| `QWEN_MODEL_EXECUTIVE` | No | `qwen-max` | Model for the Operations Manager agent |
| `CORS_ORIGINS` | No | — | Comma-separated additional CORS origins for production |
| `FRONTEND_PUBLIC_URL` | No | `http://localhost:8000` | Public backend URL sent to browser (Docker build arg) |

> **Note:** Without `DASHSCOPE_API_KEY`, agent deliberation returns structured errors. The benchmark module runs entirely on business tool simulations and does not require an API key.

---

## Demo Scenarios

The Demo Case Library includes 4 pre-configured scenarios accessed from the frontend dashboard:

| Scenario | Customer | Request | What It Demonstrates |
|---|---|---|---|
| **Standard Order** | Greenfield Municipal Council (govt, repeat) | 500 solar street lights, 14-day delivery | Happy path, multi-agent consensus |
| **Ambiguous Request** | Sunlight Initiative (NGO, budget-constrained) | "We need solar lights ASAP" | Graceful handling of incomplete information |
| **Department Deadlock** | Greenfield Municipal Council | 600 units in 7 days at min 15% margin | Cross-agent conflict, impasse detection, escalation |
| **Executive Modification** | NovaTech Solutions (first-time client) | 300 solar street lights, standard delivery | Cold-start memory, HITL constraint injection, re-deliberation |

To launch a demo: open the Demo Library page and click "Launch" on any scenario.

---

## Documentation

- **[User Guide](docs/user-guide.md)** — Full walkthrough of every feature, page, and workflow
- **[Deployment Guide](docs/deployment.md)** — Local, Docker, and production deployment
- **[Changelog](CHANGELOG.md)** — Release history and migration notes

## Key Features

### Multi-Agent Deliberation
5 operational agents assess every request from their domain perspective, then the Operations Manager synthesizes a final decision. Agents challenge each other's assumptions in a structured cross-examination round.

### Organizational Memory
A 3-tier memory system (operational, organizational, departmental) with importance-based promotion. The system remembers past decisions, customer preferences, supplier performance, and policy outcomes.

### Human-in-the-Loop Governance
Every decision goes through an approval gate. Operators can **Approve**, **Reject** with feedback, or **Modify** with strategic directives that trigger re-deliberation.

### Side-by-Side Benchmark
Compare single-agent (traditional) vs multi-agent (Orqestra) performance on any case. Measures confidence gains, risk detection improvement, factors considered, and memory utilization.

### Full Audit Trail
Every event — from case creation through deliberation, governance actions, and completion — is recorded immutably. The audit page provides searchable, expandable event history.

### Governance Replay
Step through the deliberation process with animated playback. Watch each agent's assessment, the challenge round, scoring, and adjudication unfold.

### Audit & Explainability (Decision Cards)
Every agent's assessment includes a clickable Decision Card showing reasoning, confidence, risks, factors, tools used, challenges issued/received, and consensus context. All data is derived from the immutable event store.

### Organization Health Dashboard
8 KPI cards (Cases Today, Completed, Pending Approval, Escalated, Approval Rate, Escalation Rate, Avg Confidence, Avg Deliberation Time) plus per-department performance bars with confidence scores.

### Clarification Flow
When a request is too vague (completeness < 0.70), the system identifies missing fields (amount, timeline, quantity, location, etc.), generates targeted questions, and enters a `clarification_required` state. Human answers resume deliberation.

### Failure Recovery Policy Engine
A `PolicyEngine` checks completeness/confidence thresholds, critical department status, and non-critical tolerances. Returns `can_continue`/`degraded_mode` status. Integrated into the case detail page as a Health Check button.

### Real-Time Updates
Server-Sent Events (SSE) push live updates from the backend to the frontend as deliberation progresses. The workflow graph derives live status from events during a run.

### Integration Health Dashboard
A `GET /health/integrations` endpoint reports the configured status of every integration (HubSpot, Odoo, Paystack, DHL, Qwen, Slack, SMTP). Each shows `configured` (bool) and `status` ("connected" or "not_configured"). The frontend `/admin/integrations` page renders status cards with green/amber indicators.

### Notification Management
SMTP and Slack notification channels are configurable via `GET /auth/settings/notifications` and `PUT /auth/settings/notifications`. Passwords and webhook URLs are masked in responses (`"********"`) and preserved when masked values are sent back. The notifier is reset on update so new settings take effect immediately.

### Multi-Tenancy Admin UI
The `/admin/tenants` page provides CRUD management for tenants (create, edit, delete with name/slug). The "default" tenant is protected from deletion. Slug-based routing is enforced server-side via contextvars + SQLAlchemy `do_orm_execute`.

### Analytics & Trends
`GET /dashboard/trends?days=N` (1–90) returns daily aggregates (cases_created, cases_completed, avg_confidence). The frontend renders a 14-day bar chart on the dashboard page.

### Monitoring & Observability
A lightweight in-process metrics collector tracks request counts, error rates, status code distributions, and average response duration. Exposed via `GET /metrics`. The `GET /health` endpoint verifies database connectivity. All access logs include `duration_ms` for endpoint-level performance monitoring.

---

## API Routes

### Cases
| Method | Route | Query Params | Description |
|---|---|---|---|
| GET | `/cases` | `search`, `status`, `workflow_type`, `limit`, `offset` | List / search / filter cases |
| GET | `/cases/{id}` | — | Case detail with events and directives |
| POST | `/cases` | — | Create a new case |
| POST | `/cases/{id}/run` | — | Run deliberation pipeline |
| POST | `/cases/{id}/approve` | — | Approve the decision |
| POST | `/cases/{id}/reject` | — | Reject with feedback |
| POST | `/cases/{id}/modify` | — | Inject a strategic directive |
| POST | `/cases/{id}/clarify` | — | Check if request needs clarification, generate questions |
| POST | `/cases/{id}/clarify/respond` | — | Submit answers to clarification questions |
| GET | `/cases/{id}/recovery-check` | — | Policy engine health check for a case |
| GET | `/cases/{id}/replay` | — | Replay data for a case |
| GET | `/cases/{id}/brief` | — | Decision brief summary |
| GET | `/cases/{id}/tool-results` | — | Structured tool call results grouped by tool |
| GET | `/cases/customers/search` | `q` | Search customers by name, email, or company |

### Demo, Benchmark, Dashboard, Events, Monitoring
| Method | Route | Description |
|---|---|---|
| GET | `/demo/cases` | List demo scenarios |
| POST | `/demo/launch/{scenario}` | Launch a demo scenario |
| GET | `/benchmark/{id}` | Get benchmark results |
| POST | `/benchmark/{id}/run` | Run benchmark comparison |
| GET | `/dashboard/metrics` | Aggregate KPIs (cases today, approval rate, escalation rate, avg deliberation time, department performance, etc.) |
| GET | `/dashboard/trends` | `days` | Daily aggregates for last N days (1–90) |
| GET | `/health/integrations` | — | Configuration status for all 7 integrations |
| GET | `/auth/settings/notifications` | — | Current SMTP/Slack settings (secrets masked) |
| PUT | `/auth/settings/notifications` | — | Update SMTP/Slack settings, resets notifier |
| PUT | `/auth/tenants/{id}` | — | Update a tenant's name/slug |
| DELETE | `/auth/tenants/{id}` | — | Delete a tenant (protects "default") |
| GET | `/events/stream` | — | SSE live event stream |
| GET | `/health` | — | Health check (includes DB connectivity) |
| GET | `/metrics` | — | In-memory request/error metrics |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python) |
| Frontend | Next.js 16, React 19, TypeScript |
| Styling | Tailwind CSS v4, CSS custom properties |
| Icons | lucide-react |
| Database | PostgreSQL 16 |
| Cache / Message Bus | Redis 7 |
| AI Models | Qwen3.7-Plus (operational), Qwen-Max (executive) via Alibaba Cloud DashScope |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Containerization | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio (215 tests) |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # REST endpoints (cases, demo, events, benchmark, dashboard)
│   │   ├── agents/           # AI agent definitions (sales, finance, inventory, etc.)
│   │   ├── deliberation/     # State machine, scoring, adjudication, challenge validation
│   │   ├── governance/       # Brief generation, approval handling, iteration management, clarification engine, recovery policy
│   │   ├── memory/           # 3-tier memory store, retrieval, promotion
│   │   ├── events/           # Append-only event store, Redis Pub/Sub, SSE
│   │   ├── business_tools/   # Simulated services (pricing, inventory, suppliers, policies)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Settings, database, Qwen client
│   ├── seed/                 # Demo data (customers, cases, suppliers, memories)
│   ├── alembic/              # Database migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (dashboard, demo, cases/*, admin/*)
│   │   ├── components/       # Shared UI components (Sidebar, Header, MetricCard, etc.)
│   │   ├── hooks/            # Custom React hooks (dashboard metrics, SSE events)
│   │   └── lib/              # API client, types, SSE helper
│   └── public/
├── docs/                     # Planning documentation (scope, PRD, spec, checklist)
├── docker-compose.yml
└── README.md
```

---

## License

GNU General Public License v3. See [LICENSE](LICENSE).

---

## Built For

This project was built as an entry in the **Autopilot Agent** and **Agent Society** tracks of the Alibaba Cloud AI Agent Hackathon.
