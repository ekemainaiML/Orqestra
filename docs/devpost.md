# Orqestra — Devpost Submission

## Track: Autopilot Agent + Agent Society (dual entry)

## Project Title
**Orqestra — An AI Organization, Not an AI Assistant**

## Tagline
Six Qwen-powered departments collaborate, challenge, and converge on balanced business decisions — governed by a four-stage protocol, audited by an immutable event store, and guided by organizational memory that grows with every workflow.

---

## The Core Story (100 words)

Most AI "agents" today are solo performers — a single LLM call produces an answer, but no single model has the depth of perspective that comes from specialized departmental deliberation. Orqestra reimagines AI as an organization: six specialized Qwen agents (Sales, Finance, Inventory, Procurement, Logistics, Operations Manager) process customer requests through a structured 4-stage governance protocol. Each agent thinks independently, challenges peer recommendations, and contributes to a deterministic consensus score before the Operations Manager adjudicates a final decision. The result is recommendations that account for margin requirements, delivery feasibility, supplier reliability, and policy compliance — surfaced through an executive dashboard with audit trails, side-by-side benchmarking, and governance replay.

## Key Differentiators

### 1. The 4-Stage Governance Protocol (Not Just Voting)
Agents don't vote — they **deliberate**. Independent Assessment → Cross-Agent Challenge → Consensus Scoring → Ops Manager Adjudication. The protocol catches risks a single agent would miss.

### 2. Organizational Memory (Not Just Context Windows)
Three memory layers (operational, organizational, department) persist across workflows. Run the same customer request twice — the second time, agents remember past decisions, supplier performance, and policy outcomes.

### 3. Side-by-Side Benchmark (Proving Multi-Agent > Single Agent)
Every deliberation can be compared against a single-agent baseline. Judge for yourself: Orqestra consistently finds 3x more risks, considers 2x more factors, and produces higher-confidence recommendations.

### 4. Full Auditability (Every Decision is Traceable)
The event store is the audit trail. Every agent message, every challenge, every consensus calculation is an immutable event. Click through from final decision → executive brief → consensus breakdown → individual agent reasoning.

### 5. Graceful Degradation (Not Brittle)
Agent timeout? Confidence degrades but workflow continues. Critical agent unavailable? Escalated with full trace. Only the Operations Manager failing is a hard stop. The organization keeps running.

---

## How We Built It

**Stack:** FastAPI (Python) + PostgreSQL + Redis + Next.js (TypeScript) + Qwen Cloud APIs + Alibaba Cloud

**Key architecture decisions:**
- Agents are stateless functions (not long-running processes) — an agent is a role definition + prompt + tool access, invoked per deliberation round
- The event store IS the audit trail — no separate audit service. Replay and explainability are projections of events
- Governance actions (approve/reject/modify) are state machine transitions, not special-case logic
- Scoring Engine is deterministic — Qwen provides assessments, the engine performs mathematics. Consensus scores are reproducible without calling a model
- Single PostgreSQL database — no vector DB, no analytics pipeline. Events, memories, benchmarks are all in one database

**AI Integration:**
- Operational agents (Sales, Finance, Inventory, Procurement, Logistics): `qwen3.7-plus`
- Executive agent (Operations Manager): `qwen-max`
- All communication via OpenAI-compatible SDK with structured JSON contracts (Recommendation, Challenge, Evidence)
- Agents think in natural language but communicate in typed schemas with provenance fields

**Frontend (8 routes):**
- Organization Health Dashboard (KPIs per department)
- Demo Case Library (4 pre-seeded scenarios)
- Case Detail with animated Workflow Graph + Deliberation Timeline
- Audit Trail with structured Decision Cards
- Side-by-Side Benchmark (single agent vs organization)
- Governance Replay (step-through iteration playback)
- Executive Decision Brief with Approve/Reject/Modify controls
- Manual Request Form

---

## The "Wow Moment"

**Watch what happens when agents disagree.**

Launch the "Deadlock" scenario: 600 solar street lights needed in 7 days at minimum 15% margin. The fastest supplier (AfriEnergy, 5-day lead time) charges $210/unit — violating the margin policy. The cheapest supplier (BrightPath, $155/unit) requires 250-unit minimums but has a 7-day lead time, risking the delivery deadline.

Watch the Workflow Graph branch. See Logistics challenge Procurement's cost focus with delivery risk. See Finance flag margin erosion. See the Operations Manager generate a Decision Impasse Report. The human operator can inject a strategic directive — "Prioritize delivery speed, accept lower margin" — and watch the organization re-deliberate under new constraints.

This is the moment Orqestra stops being a "multi-agent system" and starts feeling like a real organization with accountable departments.

---

## Architecture

```
Frontend (Next.js)                 Backend (FastAPI)              Infrastructure
┌─────────────────────┐          ┌──────────────────────┐       ┌──────────────┐
│ Operations Center    │          │  Deliberation Engine │       │  PostgreSQL  │
│ Executive Brief      │ ◄─SSE── │  ┌─────────────────┐ │       │  • Cases     │
│ Audit View           │          │  │ Agent Manager    │ │       │  • Events    │
│ Benchmark View       │          │  │ Challenge Valid  │ │       │  • Memories  │
│ Governance Replay    │          │  │ Scoring Engine   │ │       │  • Benchmarks│
│ Demo Case Library    │          │  │ Adjudicator      │ │       └──────────────┘
└─────────────────────┘          │  │ State Machine    │ │       ┌──────────────┐
                                 │  └─────────────────┘ │       │    Redis     │
                                 │                      │       │  • Pub/Sub   │
                                 │  ┌─────────────────┐ │       │  • SSE Bus   │
                                 │  │  Governance     │ │       └──────────────┘
                                 │  │  Memory         │ │       ┌──────────────┐
                                 │  │  Events         │ │       │  Qwen Cloud  │
                                 │  └─────────────────┘ │       │  • qwen3.7   │
                                 └──────────────────────┘       │  • qwen-max  │
                                                                 └──────────────┘
```

---

## Screenshots to Include

1. **Dashboard** — Organization Health Dashboard with KPIs (cases today, avg confidence, escalation rate)
2. **Workflow Graph** — Case detail with animated state machine showing current position
3. **Deliberation Timeline** — Real-time event stream with agent recommendations
4. **Audit Trail** — Full event history with structured Decision Cards
5. **Benchmark Comparison** — Side-by-side: single agent vs Orqestra
6. **Governance Replay** — Step-through iteration playback
7. **"Wow Moment"** — The deadlock scenario with the workflow graph branching, red status indicators, and the Decision Impasse Report

---

## Demo Video Script (90 seconds)

| Time | Visual | Audio |
|------|--------|-------|
| 0:00 | Dashboard | "Orqestra is an AI organization — six Qwen-powered departments working together." |
| 0:10 | Demo Library | "Launch any scenario. Let's try a standard order — 500 solar street lights." |
| 0:20 | Workflow Graph | "Watch the state machine: memory retrieval, independent assessment, challenge round..." |
| 0:35 | Agent Cards | "Each department thinks independently. Sales assesses customer intent, Finance checks margin, Logistics validates delivery." |
| 0:45 | Challenge Round | "Agents challenge each other. Logistics flags a delivery risk Finance overlooked." |
| 0:55 | Consensus + Decision | "The Scoring Engine aggregates across 5 dimensions. Operations Manager adjudicates." |
| 1:05 | Executive Brief | "Approve, Reject, or Modify. Each governance iteration is numbered and auditable." |
| 1:15 | Benchmark | "Side-by-side: single agent found 2 risks. Orqestra found 5." |
| 1:25 | Deadlock Scenario | "Watch what happens when agents can't agree — this is the wow moment." |
| 1:40 | Close | "Orqestra. An AI organization, not an AI assistant." |

---

## What's Next

- Additional business domains (returns, HR, marketing)
- Real third-party integrations (ERP, CRM, payment gateways)
- Autonomous execution after human approval
- Historical benchmark analytics and leaderboards
- Multi-language support
- Notification system (email/Slack for escalations)

---

## Links

- **Deployed URL:** [Alibaba Cloud URL]
- **GitHub:** [https://github.com/your-org/orqestra](https://github.com/your-org/orqestra)
- **Demo Video:** [YouTube URL]

---

## Built With

- Qwen Cloud (qwen3.7-plus, qwen-max)
- FastAPI
- PostgreSQL
- Redis
- Next.js
- TypeScript
- Tailwind CSS
- Docker
- Alibaba Cloud
