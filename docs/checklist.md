# Orqestra — Build Checklist

**Mode:** Autonomous  
**Rule:** No new features after Item 7 (Deliberation Engine). Everything after is integration, UI, deployment, testing, submission.

| # | Item | Status |
|---|---|---|---|
| 1 | Backend scaffold (FastAPI, SQLAlchemy models, Alembic, `.env`) | ✓ |
| 2 | Seed data & migrations (demo cases, customers, suppliers, memories) | ✓ |
| 3 | Qwen client (OpenAI-compatible SDK, tiered model routing) | ✓ |
| 4 | Agent definitions (6 agents + registry + base contract) | ✓ |
| 5 | Business tools (simulated Inventory, Pricing, SupplierDB, Policy) | ✓ |
| 6 | Memory Engine (Memory Service, Promotion Policy, 3-layer queries) | ✓ |
| 7 | Deliberation Engine (Agent Manager, Challenge Validator, Scoring Engine, Adjudicator, State Machine) | ✓ |
| 8 | Events Layer (Event Store, Publisher/SSE, Projections) | ✓ |
| 9 | Governance Engine (Brief Generator, Approval Handler, Iteration Manager) | ✓ |
| 10 | REST API (case CRUD, demo launch, governance, SSE, benchmark, dashboard) | ✓ |
| 11 | Frontend (Next.js, 8 pages, 10 components, SSE client, types) | ✓ |
| 12 | Replay Mode (event replay endpoint, workflow replay page, iteration playback) | ✓ |
| 13 | Deployment (Alibaba Cloud ECS, RDS, Redis, env config, verification) | ✓ |
| 14 | Devpost submission assets (story, screenshots, wow moment, optional deploy URL) | ✓ |
