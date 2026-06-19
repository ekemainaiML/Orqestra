# Orqestra — Technical Spec

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI (Python 3.11+) | Async-native, Pydantic integration, fast dev velocity, ideal for agent orchestration |
| Database | PostgreSQL | ACID guarantees, JSONB for flexible payloads, pgvector for future embeddings, strong reporting |
| Cache / message bus | Redis | Workflow state, Pub/Sub event bus, SSE backplane, job queues |
| Frontend | Next.js 14+ (App Router) + React + TypeScript | Dashboard-centric demo, SSR optional, excellent ecosystem |
| AI reasoning | Qwen Cloud APIs (OpenAI-compatible SDK) | Hackathon requirement; `qwen3.7-plus` for operational agents, `qwen-max` for Operations Manager |
| Deployment | Alibaba Cloud (ECS + RDS + Redis) | Hackathon requirement |
| ORM | SQLAlchemy 2.0 (async) | Mature async support, Alembic migrations |
| Real-time | Server-Sent Events (SSE) via Redis Pub/Sub | One-way streaming sufficient for timeline updates; simpler than WebSockets |

## Runtime & Deployment

- **Deployment target:** Deployed URL on Alibaba Cloud (ECS for backend, frontend on Alibaba Cloud or Vercel). Local fallback for development.
- **Environment requirements:** Python 3.11+, Node.js 18+, `DASHSCOPE_API_KEY` (Qwen Cloud), PostgreSQL connection string, Redis URL.
- **Demo reliability:** Replay mode using recorded event streams as backup if Qwen API is unavailable during judging.
- **Demo Case Library:** 4 pre-seeded scenarios launched instantly — no live email dependency.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Operations│ │Executive │ │  Audit   │ │Benchmrk│ │
│  │  Center  │ │  Brief   │ │   View   │ │  View  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │            │            │            │       │
│       └────────────┴─────┬──────┴────────────┘       │
│                          │ SSE stream                │
└──────────────────────────┼───────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────┐
│              Backend (FastAPI)                        │
│                          │                            │
│                  ┌───────┴───────┐                   │
│                  │   API Layer   │                   │
│                  │ (REST + SSE)  │                   │
│                  └───────┬───────┘                   │
│                          │                            │
│  ┌──────────┐ ┌─────────┼──────────┐ ┌───────────┐   │
│  │Governance│ │      Deliberation   │ │  Memory   │   │
│  │  Engine  │ │        Engine      │ │  Engine   │   │
│  │          │ │  ┌────────────────┐ │ │           │   │
│  │ • Brief  │ │  │ Agent Manager  │ │ │ Retrieval │   │
│  │ • Approv │ │  │ Challenge Valid│ │ │ Promotion │   │
│  │ • Modif  │ │  │ Scoring Engine │ │ │    +      │   │
│  │ • Iterat │ │  │ Adjudicator    │ │ │ Queries   │   │
│  │          │ │  │ State Machine  │ │ │           │   │
│  └────┬─────┘ │  └────────────────┘ │ └─────┬─────┘   │
│       │       └──────────┬──────────┘       │         │
│       │                  │                  │         │
│  ┌────┴──────────────────┴──────────────────┴─────┐   │
│  │                 Events Layer                    │   │
│  │         Event Store + Publisher + SSE           │   │
│  └────────────────────┬───────────────────────────┘   │
│                       │                                │
│  ┌────────────────────┼───────────────────────────┐   │
│  │  PostgreSQL        │  Redis                    │   │
│  │  • Cases           │  • Workflow State         │   │
│  │  • Events          │  • Pub/Sub Channels       │   │
│  │  • Memories        │  • Session Cache          │   │
│  │  • Benchmarks      │                           │   │
│  │  • Directives      │                           │   │
│  └────────────────────┴───────────────────────────┘   │
│                       │                                │
│              ┌────────┴────────┐                       │
│              │   Qwen Cloud    │                       │
│              │  • qwen3.7-plus │   6 per-case calls    │
│              │  • qwen-max     │   1 per-case call     │
│              └─────────────────┘                       │
└────────────────────────────────────────────────────────┘
```

## Component Architecture

### Deliberation Engine (`app/deliberation/`)

Implements: `prd.md > Organizational Deliberation`, `prd.md > Failure Recovery & Resilience`

#### Agent Manager

- Loads agents from `AgentRegistry` for the current workflow type
- Assembles per-agent context: case data, department objectives, retrieved memory, tool outputs, policies
- Triggers parallel Qwen API calls for all agents
- Handles retries (3 attempts: immediate, 10s, 30s)
- Handles timeouts — records agent as `unavailable`, workflow continues with confidence degradation
- Collects structured recommendations (Pydantic-validated)
- Emits `RECOMMENDATION_SUBMITTED` events

#### Challenge Validator

- Routes recommendations to peer agents for review
- Validates that challenges include required fields: `challenge_type`, `target_agent`, `statement`, `evidence`, `confidence`
- Records validated challenges as `CHALLENGE_ISSUED` events
- Invalid challenges rejected with reason

#### Scoring Engine

- Deterministic — takes agent assessments as input, performs mathematics
- Evaluates each proposal across 5 dimensions: Customer Satisfaction, Profitability, Operational Risk, Delivery Reliability, Policy Compliance
- Each agent contributes scores only within its expertise domain
- Aggregates into per-proposal consensus scores
- Emits `CONSENSUS_CALCULATED` event with full score breakdown

#### Adjudicator

- Uses `qwen-max` (the only agent using the larger model)
- Input: all recommendations, challenges, evidence, consensus scores, policies
- Output: selected strategy, one-sentence rationale, confidence score, list of rejected alternatives with reasons
- If tied scores or policy conflicts: generates Decision Impasse Report instead, transitions to `ESCALATED`
- Emits `DECISION_GENERATED` event

#### State Machine

- The single source of truth for workflow state
- States:
  - `CREATED` → `MEMORY_RETRIEVAL` → `INDEPENDENT_ASSESSMENT` → `CHALLENGE_ROUND` → `CONSENSUS_SCORING` → `ADJUDICATION` → `APPROVAL_PENDING`
  - Alternative paths: `CLARIFICATION_REQUIRED`, `ESCALATED` (deadlock/policy conflict), `REJECTED`, `FAILED` (Ops Manager failure)
  - Terminal states: `COMPLETED`, `CLOSED`, `ESCALATED`, `CLOSED_WITHOUT_RESOLUTION`
- Each state transition emits a corresponding event
- After `MODIFY` governance action: transitions to `CONSTRAINT_MODIFIED` → `REDELIBERATION_PENDING` → back through the main flow

### Governance Engine (`app/governance/`)

Implements: `prd.md > Executive Governance`

#### Brief Generator

- After Adjudicator produces a decision, generates the Executive Decision Brief
- Brief fields: Case ID, Customer, Request Summary, Recommended Strategy, Rationale, Confidence, Consensus Breakdown, Business Impact (revenue, margin, delivery confidence, risk level), Key Risks, Memory Evidence, Audit Status, Governance Actions available
- The brief answers 8 questions (see `prd.md > Executive Governance` ACs)

#### Approval Handler

- Three endpoints: `POST /cases/{id}/approve`, `POST /cases/{id}/reject`, `POST /cases/{id}/modify`
- Each is a state transition in the State Machine, not special-case logic
- On `modify`: stores directive in `directives` table, creates new governance iteration, transitions to `CONSTRAINT_MODIFIED`
- On `reject`: transitions to `REJECTED`, workflow closes
- On `approve`: transitions to `APPROVED` → `EXECUTED` → `COMPLETED`

#### Iteration Manager

- Tracks governance iteration number (starting at 0)
- Each modification creates Iteration N+1
- Maintains full history of all iterations for replay
- After 3+ iterations: emits `GOVERNANCE_WARNING` but does not hard-limit

### Memory Engine (`app/memory/`)

Implements: `prd.md > Incoming Request & Workflow Initiation` (memory retrieval), `prd.md > Organizational Deliberation`

#### Memory Service

- Single governed entry point for all memory access
- Agents do not query databases directly — they call the Memory Service
- Input: `agent_id`, `query_type`, `entity` (customer/supplier/etc.)
- Pipeline: intent detection → memory search → relevance ranking → context assembly
- Returns compact memory package limited to what's relevant for the decision
- Emits `MEMORY_RETRIEVED` event with count and sources

#### Memory Promotion Policy

- Not every event becomes a memory — only significant events
- Promoted to memory: major customer decisions, successful negotiations, supplier failures, policy exceptions, escalations, deadlocks, human overrides
- Remains audit log only: every message, routine approvals, temporary calculations
- Importance scoring: business impact, financial impact, human involvement, decision uniqueness, reuse potential

#### Three Memory Layers

1. **Operational Data** — Structured business records (customers, orders, inventory) in PostgreSQL
2. **Organizational Memory** — Experiences from previous workflows (lessons learned, past decisions)
3. **Department Memory** — Per-agent specialized knowledge (Sales: negotiation patterns, Finance: credit risks)

### Events Layer (`app/events/`)

Implements: `prd.md > Audit & Explainability`

#### Event Store

- Immutable append-only log of all workflow events
- Schema: `id`, `case_id`, `iteration`, `event_type`, `actor` (agent_id or "operator"), `payload` (JSONB), `timestamp`
- Event types: `CASE_CREATED`, `MEMORY_RETRIEVED`, `RECOMMENDATION_SUBMITTED`, `CHALLENGE_ISSUED`, `CONSENSUS_CALCULATED`, `DECISION_GENERATED`, `BRIEF_PRESENTED`, `DECISION_APPROVED`, `DECISION_REJECTED`, `CONSTRAINT_MODIFIED`, `ITERATION_STARTED`, `WORKFLOW_COMPLETED`, `AGENT_UNAVAILABLE`, `WORKFLOW_ESCALATED`
- The full audit trail is a `SELECT ... WHERE case_id = ? ORDER BY timestamp;`

#### Publisher

- Writes events to PostgreSQL (persistence) and Redis Pub/Sub (real-time)
- SSE stream subscribes to Redis channel and fans out to dashboard clients

#### Projections

- Dashboard metrics are projections of events (aggregate queries, cached in Redis)
- No separate analytics pipeline — just `COUNT`, `AVG`, `GROUP BY` on the event store

### Agent Definitions (`app/agents/`)

Implements: `prd.md > Organizational Deliberation`

#### Base Agent Contract

```python
class BaseAgent(ABC):
    role: str
    model: str  # qwen3.7-plus default, qwen-max for Ops Manager
    objectives: list[str]
    policies: list[str]
    tools: list[str]

    @abstractmethod
    async def assess(case_context, memory, tool_outputs) -> AgentRecommendation: ...
```

#### Registered Agents

| Agent | Model | Core Objective |
|---|---|---|
| Sales | qwen3.7-plus | Interpret customer intent, generate quotation |
| Inventory | qwen3.7-plus | Check stock availability |
| Procurement | qwen3.7-plus | Identify suppliers, sourcing options |
| Finance | qwen3.7-plus | Evaluate risk, profitability, margin |
| Logistics | qwen3.7-plus | Validate delivery feasibility |
| Operations Manager | qwen-max | Synthesize, adjudicate, decide |

### Workflows (`app/workflows/`)

Implements: `prd.md > Incoming Request & Workflow Initiation`

- Each workflow type defines which agents participate and their objectives
- MVP: `OrderFulfillmentWorkflow` (Sales, Inventory, Procurement, Finance, Logistics, Ops Manager)
- Future: `CustomerSuccessWorkflow`, `ProcurementPlanningWorkflow`
- Enables the Agent Registry pattern: `registry.get_agents(workflow_type="order_fulfillment")`

### Resilience Policy Module (`app/resilience/`)

Implements: `prd.md > Failure Recovery & Resilience`

#### Policy Engine

- Centralized thresholds (not scattered across code):
  ```yaml
  critical_agents: [finance, logistics, inventory]
  max_retries: 3
  retry_delays: [0, 10, 30]  # seconds
  minimum_completeness: 0.75
  minimum_confidence: 0.65
  ```
- `can_continue(case) → bool, reason`: checks completeness and confidence thresholds
- If critical agent unavailable → `ESCALATED`
- If non-critical agent unavailable → proceed with warning + confidence degradation
- Ops Manager failure = hard stop (governance unavailable)

### Business Tools (`app/business_tools/`)

Implements: `prd.md > Organizational Deliberation` (tool invocation)

- Simulated services for the demo: `InventoryService`, `PricingEngine`, `SupplierDB`, `PolicyEngine`
- Each returns structured JSON that agents use as evidence
- Tools have controlled failure modes for resilience testing

## Data Model

### Cases
| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| customer_id | UUID | FK → customers |
| request_text | text | Raw customer request |
| status | enum | State machine state |
| iteration | int | Current governance iteration |
| workflow_type | string | "order_fulfillment" |
| confidence | float | Current organizational confidence |
| completeness | float | Organizational Completeness Score |
| created_at | timestamptz | |
| completed_at | timestamptz | nullable |

### Workflow Events
| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| case_id | UUID | FK → cases |
| iteration | int | Governance iteration |
| event_type | string | See event types above |
| actor | string | agent_id or "operator" |
| payload | JSONB | Event-specific data |
| timestamp | timestamptz | |

### Memories
| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| memory_type | enum | operational / organizational / department |
| domain | string | customer / supplier / policy / decision |
| entity_id | string | Reference to business entity |
| content | JSONB | The memory payload |
| importance | float | 0-100 |
| department | string | nullable, for department memory |
| agent_id | string | nullable, for department memory |
| created_at | timestamptz | |

### Directives
| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| case_id | UUID | FK → cases |
| iteration | int | |
| directive_type | string | minimum_margin / delivery_priority / supplier_restriction |
| value | JSONB | |
| issued_by | string | "operator" |
| created_at | timestamptz | |

### Benchmark Runs
| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| case_id | UUID | FK → cases |
| run_type | enum | single_agent / organization |
| recommendation | JSONB | |
| confidence | float | |
| risks_found | int | |
| factors_considered | int | |
| reasoning_time_s | float | |
| memory_used | int | |
| created_at | timestamptz | |

## File Structure

```
orqestra/
├── docs/                          # Hackathon artifacts
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   └── spec.md
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/              # DB migrations
│   │
│   ├── seed/                      # Demo seed data
│   │   ├── demo_cases.json
│   │   ├── customers.json
│   │   ├── suppliers.json
│   │   └── memories.json
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entry, lifespan, router mounts
│   │   │
│   │   ├── api/                   # HTTP endpoints
│   │   │   ├── __init__.py
│   │   │   ├── cases.py           # CRUD + governance (approve/reject/modify)
│   │   │   ├── demo.py            # Demo case library launch
│   │   │   ├── events.py          # SSE stream endpoint
│   │   │   ├── benchmark.py       # Benchmark comparison endpoint
│   │   │   └── dashboard.py       # Health dashboard aggregate metrics
│   │   │
│   │   ├── deliberation/          # Organizational decision-making core
│   │   │   ├── __init__.py
│   │   │   ├── agent_manager.py   # Agent lifecycle, parallel Qwen calls
│   │   │   ├── challenge_validator.py
│   │   │   ├── scoring_engine.py  # Deterministic consensus aggregation
│   │   │   ├── adjudicator.py     # Ops Manager (qwen-max) synthesis
│   │   │   └── state_machine.py   # State transitions
│   │   │
│   │   ├── governance/            # Executive governance
│   │   │   ├── __init__.py
│   │   │   ├── brief_generator.py # Executive Decision Brief
│   │   │   ├── approval_handler.py # Approve/Reject/Modify
│   │   │   └── iteration_manager.py
│   │   │
│   │   ├── memory/                # Organizational memory
│   │   │   ├── __init__.py
│   │   │   ├── memory_service.py  # Retrieval + storage pipeline
│   │   │   ├── memory_promotion.py # Promotion policy + importance scoring
│   │   │   └── queries.py         # Memory search queries
│   │   │
│   │   ├── events/                # First-class event system
│   │   │   ├── __init__.py
│   │   │   ├── event_store.py     # Immutable append-only event log
│   │   │   ├── publisher.py       # Redis Pub/Sub + SSE fan-out
│   │   │   └── projections.py     # Aggregate queries for dashboard
│   │   │
│   │   ├── workflows/             # Workflow-type definitions
│   │   │   ├── __init__.py
│   │   │   └── order_fulfillment.py  # Agent roster for this workflow
│   │   │
│   │   ├── agents/                # Agent role definitions
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Abstract agent contract
│   │   │   ├── registry.py        # Agent registry
│   │   │   ├── sales.py
│   │   │   ├── finance.py
│   │   │   ├── inventory.py
│   │   │   ├── procurement.py
│   │   │   ├── logistics.py
│   │   │   └── operations_manager.py
│   │   │
│   │   ├── resilience/            # Graceful degradation
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # YAML thresholds
│   │   │   └── policy_engine.py   # can_continue(), retry logic
│   │   │
│   │   ├── business_tools/        # Simulated business services
│   │   │   ├── __init__.py
│   │   │   ├── inventory_service.py
│   │   │   ├── pricing_engine.py
│   │   │   ├── supplier_db.py
│   │   │   └── policy_engine.py
│   │   │
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── case.py
│   │   │   ├── workflow_event.py
│   │   │   ├── memory.py
│   │   │   ├── benchmark_run.py
│   │   │   └── directive.py
│   │   │
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── case.py
│   │   │   ├── event.py
│   │   │   ├── governance.py
│   │   │   └── benchmark.py
│   │   │
│   │   └── services/              # Shared infrastructure
│   │       ├── __init__.py
│   │       └── qwen_client.py     # Qwen Cloud API wrapper (OpenAI SDK)
│   │
│   ├── tests/
│   │   ├── test_deliberation.py
│   │   ├── test_governance.py
│   │   └── test_memory.py
│   │
│   └── .env.example
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Organization Health Dashboard
│   │   │   ├── cases/
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx       # Case detail + WorkflowGraph
│   │   │   │   │   ├── audit/
│   │   │   │   │   │   └── page.tsx   # Audit trail + Decision Cards
│   │   │   │   │   ├── benchmark/
│   │   │   │   │   │   └── page.tsx   # Side-by-side comparison
│   │   │   │   │   └── replay/
│   │   │   │   │       └── page.tsx   # Governance iteration replay
│   │   │   │   └── new/
│   │   │   │       └── page.tsx       # Manual request form
│   │   │   └── demo/
│   │   │       └── page.tsx           # Demo Case Library
│   │   │
│   │   ├── components/
│   │   │   ├── WorkflowGraph.tsx       # Center: animated workflow visualization
│   │   │   ├── DeliberationTimeline.tsx # Right panel: event stream
│   │   │   ├── DecisionBoard.tsx       # Left panel: business state
│   │   │   ├── AgentCard.tsx           # Per-agent status + reasoning
│   │   │   ├── ExecutiveBrief.tsx      # Executive Decision Brief
│   │   │   ├── GovernanceActions.tsx   # Approve/Reject/Modify
│   │   │   ├── BenchmarkComparison.tsx # Side-by-side comparison
│   │   │   ├── MemoryPanel.tsx         # Memory retrieval display
│   │   │   ├── HealthMetrics.tsx       # Dashboard KPIs
│   │   │   └── WorkflowReplay.tsx      # Governance iteration scrubber
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                  # API client
│   │   │   ├── sse.ts                  # SSE event client
│   │   │   └── types.ts
│   │   │
│   │   └── hooks/
│   │       ├── useCaseEvents.ts
│   │       └── useDashboardMetrics.ts
│   │
│   └── public/
│
├── process-notes.md
├── .env.example
└── README.md
```

## Key Technical Decisions

1. **Agents as stateless functions, not long-running processes.** An agent is a role definition + prompt + tool access, not a persistent service. This eliminates worker management, inter-agent RPC, and service discovery complexity.
2. **Event store as the audit trail.** No separate audit service. Every state transition and agent message is an immutable event. The full audit trail is a filtered query on `workflow_events`. Replay and explainability come for free.
3. **Governance as state machine transitions.** Approve, Reject, and Modify are not special-case business logic — they're state transitions in the Deliberation State Machine. This keeps the architecture unified and testable.
4. **Scoring Engine is deterministic.** Qwen provides assessments; the Scoring Engine performs mathematics. Consensus scores are reproducible and explainable without calling a model.
5. **Deliberation Engine is the core product, not the agents.** The orchestration, governance, and decision-making protocol is the innovation. Agents, dashboard, and Qwen are supporting components.
6. **Single database (PostgreSQL) for MVP.** No vector DB, no analytics DB, no document store. PostgreSQL handles operational data, events, memories, and aggregates. pgvector deferred.

## Dependencies & External Services

| Dependency | Purpose | Docs | Notes |
|---|---|---|---|
| Qwen Cloud API | Agent reasoning | [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/first-api-call) | OpenAI-compatible SDK; base_url: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| FastAPI | Backend framework | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) | async, Pydantic v2 |
| SQLAlchemy 2.0 | ORM | [docs.sqlalchemy.org](https://docs.sqlalchemy.org/en/20/) | async session support |
| Alembic | Migrations | [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/) | |
| Redis py | Redis client | [redis-py docs](https://redis-py.readthedocs.io/) | async Pub/Sub |
| fastapi-sse-events | SSE streaming | [pypi.org/project/fastapi-sse-events](https://pypi.org/project/fastapi-sse-events/) | Redis Pub/Sub → SSE |
| Next.js | Frontend | [nextjs.org](https://nextjs.org/docs) | App Router |
| Tailwind CSS | Styling | [tailwindcss.com](https://tailwindcss.com/docs) | |
| Alibaba Cloud | Hosting | [aliyun.com](https://www.aliyun.com/) | ECS, RDS, Redis |

## Open Issues

- **Qwen model selection for tiered agents:** `qwen3.7-plus` proposed for operational agents, `qwen-max` for Ops Manager. Confirm model availability and pricing on the learner's Qwen Cloud plan before build.
- **Confidence threshold for Organizational Completeness Score:** 75% proposed for auto-proceed. May need tuning after initial testing.
- **Replay mode implementation:** Is replay a static JSON playback or does the State Machine re-execute from stored events? Currently designed as event replay from `workflow_events` table — confirm this approach during build.
- **Frontend SSE reconnection strategy:** Auto-reconnect with exponential backoff. Confirm approach during build.
