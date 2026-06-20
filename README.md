# Orqestra

**Autonomous AI Workforce for Business Operations**

Orqestra is an AI-powered platform where specialized agents — Sales, Finance, Inventory, Procurement, Logistics, and an Operations Manager — collaborate as digital departments to automate customer order fulfillment. It uses a 4-stage governance protocol (Independent Assessment → Challenge → Consensus → Adjudication) with human-in-the-loop approval, organizational memory, and full audit trails.

---

## Overview

| Department | Agent | Model | Role |
|---|---|---|---|
| Sales | Sales Agent | qwen3.7-plus | Interpret customer intent, generate quotations |
| Finance | Finance Agent | qwen3.7-plus | Evaluate profitability, financial risk, policy compliance |
| Inventory | Inventory Agent | qwen3.7-plus | Check stock availability, assess make-vs-buy |
| Procurement | Procurement Agent | qwen3.7-plus | Identify suppliers, evaluate sourcing options |
| Logistics | Logistics Agent | qwen3.7-plus | Validate delivery feasibility, shipping risk |
| Executive | Operations Manager | qwen-max | Synthesize inputs, adjudicate conflicts, final decision |

**Demo workflow:** Customer orders 500 solar-powered street lights with 14-day delivery. Agents deliberate, the Operations Manager adjudicates, and a human operator approves, rejects, or modifies the decision.

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

# Ensure PostgreSQL and Redis are running, then:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

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
| `QWEN_MODEL_OPERATIONAL` | No | `qwen3.7-plus` | Model for operational agents |
| `QWEN_MODEL_EXECUTIVE` | No | `qwen-max` | Model for the Operations Manager agent |

> **Note:** Without `DASHSCOPE_API_KEY`, agent deliberation falls back gracefully with structured errors. The benchmark module runs entirely on business tool simulations and does not require an API key.

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

### Real-Time Updates
Server-Sent Events (SSE) push live updates from the backend to the frontend as deliberation progresses.

---

## API Routes

### Cases
| Method | Route | Description |
|---|---|---|
| GET | `/cases` | List all cases |
| GET | `/cases/{id}` | Case detail with events and directives |
| POST | `/cases` | Create a new case |
| POST | `/cases/{id}/run` | Run deliberation pipeline |
| POST | `/cases/{id}/approve` | Approve the decision |
| POST | `/cases/{id}/reject` | Reject with feedback |
| POST | `/cases/{id}/modify` | Inject a strategic directive |
| GET | `/cases/{id}/replay` | Replay data for a case |
| GET | `/cases/{id}/brief` | Decision brief summary |

### Demo, Benchmark, Dashboard, Events
| Method | Route | Description |
|---|---|---|
| GET | `/demo/cases` | List demo scenarios |
| POST | `/demo/launch/{scenario}` | Launch a demo scenario |
| GET | `/benchmark/{id}` | Get benchmark results |
| POST | `/benchmark/{id}/run` | Run benchmark comparison |
| GET | `/dashboard/metrics` | Aggregate KPIs |
| GET | `/events/stream` | SSE live event stream |
| GET | `/health` | Health check |

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
| Testing | pytest, pytest-asyncio |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # REST endpoints (cases, demo, events, benchmark, dashboard)
│   │   ├── agents/           # AI agent definitions (sales, finance, inventory, etc.)
│   │   ├── deliberation/     # State machine, scoring, adjudication, challenge validation
│   │   ├── governance/       # Brief generation, approval handling, iteration management
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
│   │   ├── app/              # Next.js pages (dashboard, demo, cases/*, etc.)
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
