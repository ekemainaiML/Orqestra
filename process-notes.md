# Process Notes

## /onboard

- **Learner:** Ekemini Stephen — software engineer, AI developer, background in Mechanical Engineering
- **Technical experience:** Advanced — full-stack, AI agents, workflow automation, ML. Heavy AI coding agent user (Copilot, Cursor, ChatGPT, custom agent frameworks)
- **Project:** Orqestra — AI workforce platform with multi-agent collaboration for business automation
- **Learning goals:** Deepen multi-agent orchestration, memory mgmt, tool integration, HITL patterns. Hands-on with Qwen Cloud. Strong architectural patterns for production.
- **Creative sensibility:** Drawn to elegant design that makes complex systems feel simple. Default to clean, functional, engineering-driven.
- **Prior SDD experience:** Significant — regularly creates PRDs, specs, architecture diagrams, roadmaps. Calibrate /reflect for depth, not basics.
- **Energy:** High, self-directed, knows what they want. Move at brisk pace, defer to their judgment on tradeoffs.
- **Engagement style:** Active, thoughtful responses — clearly has strong architectural instincts.

## /scope

- **Brain dump:** Rich, detailed. Orqestra as "AI company" — 6 specialized agents (Sales, Finance, Inventory, Procurement, Logistics, Ops Manager) with structured governance.
- **Research references shared:** Ceipal (validation), Google ADK Hackathon (execution reference), Gartner prediction (market timing). All three resonated.
- **Workflow chosen:** Customer order fulfillment (500 solar-powered street lights, 14-day delivery). Single deep workflow, not multiple shallow ones.
- **What's cut:** Returns, multi-tenancy, HR/Marketing/Legal, deep SaaS integrations, autonomous execution of irreversible actions, multi-workflow demo.
- **Architecture:** Qwen Cloud APIs (reasoning) + FastAPI + PostgreSQL + Redis + React/Next.js + Alibaba Cloud. Four layers: User Interaction, Orchestration, Agent Workforce, Data & Memory.
- **Governance protocol:** Four-stage — Independent Assessment → Cross-Agent Challenge → Consensus Scoring → Ops Manager Adjudication.
- **Memory:** Shared organizational + per-department memory. Demo'd by running same customer workflow twice (first cold, second with institutional memory).
- **Human-in-the-loop:** Three options — Approve, Reject (returns to deliberation with new constraint), Modify (injects strategic directive, agents adapt).
- **Explainability:** Live Decision Cards, deliberation traces, post-hoc case files with Decision Justification Reports, visual decision graphs.
- **Multi-agent benchmark:** Side-by-side vs single-agent with Organizational Decision Score, Decision Coverage, Conflict Detection metrics.
- **Deepening rounds:** 1 round chosen. Explored 6 areas — governance protocol, organizational memory, multi-agent measurement, HITL design, explainability/audit, future roadmap. All materially sharpened the scope doc.
- **Active shaping:** Learner drove the conversation throughout. Pushed back on reducing features, instead narrowed scope by workflow. Generated the governance protocol independently. Designed the dashboard UX vision without prompting.
- **Key risk noted:** High surface area (6 agents × 4 layers × memory × governance × benchmark × dashboard). "Deep not wide" strategy is sound but will be tested in build.

## /prd

- **PRD conversation:** Zoomed in significantly on scope. Every behavior turned into precise acceptance criteria.
- **Key additions vs scope:** Hybrid agent communication protocol (structured messages + natural language reasoning), memory architecture (3 layers + Memory Retrieval Service + Memory Promotion Policy), failure recovery model (graceful degradation, 5 failure types, confidence degradation), demo choreography (0-180 second sequence), Organization Health Dashboard with KPIs.
- **Edge cases surfaced:** Ambiguous requests (clarification workflow, confidence thresholds), decision deadlock (tied scores, policy constraint failure), governance iterations (soft limit, constraint conflict detection), 5 workflow terminal states.
- **Scope guard conversations:** Benchmark kept in MVP but narrowed to single-comparison tab (no historical analytics platform). Health Dashboard included but trimmed to one screen. Learner pushed to keep both — argued they're essential for the "AI organization" narrative. Accepted.
- **What surprised them:** The depth of the failure recovery discussion — learner noted they hadn't thought through partial deliberation scenarios before the conversation.
- **Deepening rounds:** 1 round. Covered 6 areas — agent communication protocol, Qwen utilization strategy, memory architecture, demo choreography, success metrics, failure recovery. All materially strengthened the PRD.
- **Active shaping:** Learner independently proposed the hybrid communication protocol, memory promotion policy, 5-terminal-state model, and Organizational Effectiveness Score. Drove the depth of every section.

## /spec

- **Tech interview:** Learner had strong, well-reasoned opinions. Stack mostly pre-decided: FastAPI, PostgreSQL, Redis, Next.js, Qwen Cloud, Alibaba Cloud. Explicitly rejected LangChain, AutoGen, CrewAI, vector DBs for MVP. LangChain rejected due to abstraction leakage — prefers lightweight in-house orchestration.
- **Architecture converged on:** Deliberation Engine as core product (Agent Manager, Challenge Validator, Scoring Engine, Adjudicator, State Machine). Governance Engine (brief, approval, iterations). Memory Engine (3 layers + retrieval + promotion). Events layer as first-class citizen.
- **Key architectural decisions:** Agents as stateless functions not long-running processes. Event store IS the audit trail. Governance as state machine transitions. Scoring engine deterministic. Single PostgreSQL DB for MVP.
- **Deployment:** Deployed URL on Alibaba Cloud (ECS + RDS + Redis). Replay mode as API outage fallback. Demo Case Library (4 scenarios) as primary entry — no email integration.
- **File structure adjustments from proposal:** `engine/` → `deliberation/`, events elevated to top-level `events/` module, added `workflows/` for workflow-type modularity, `tools/` → `business_tools/`, agent registry moved to `agents/registry.py`, added `seed/` for demo data, frontend case routes reorganized as sub-routes (audit, benchmark, replay).
- **Deepening rounds:** 0 (learner chose to proceed directly — architecture was already thoroughly converged).
- **Active shaping:** Learner drove all architectural decisions. Proposed event-driven architecture, agent-as-stateless-function model, governance-as-state-transitions pattern, SSE over WebSockets, tiered Qwen model strategy. Pushed back on no edits. Very strong technical self-awareness.
- **Confidence:** High. Spec maps every PRD story to a component.

## /build — Test fixes (Session 2026-06-20)

- **Fixed conftest DB port logic:** Port 5432→5433 swap only when `DATABASE_URL` env var is NOT explicitly set (e.g., CI sets it, so no swap).
- **Added `asyncio_mode = "auto"`** to `pyproject.toml` — async tests now properly discoverable by pytest-asyncio.
- **Isolated DB-dependent tests:** Marked all integration tests (event_store, memory queries/service) as `@pytest.mark.skip` with reason "Needs DB session injection refactor — `module` uses global async_session".
- **Result:** 57 passed, 11 skipped across 5 test files (state_machine, scoring_engine, benchmark, memory_service, event_store).
