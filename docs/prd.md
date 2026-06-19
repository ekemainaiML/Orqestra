# Orqestra — Product Requirements Document

## Problem Statement
Business operations teams managing complex multi-department workflows — order fulfillment, procurement, logistics, finance coordination — currently rely on fragmented tools (email, spreadsheets, ERPs) or single AI assistants that lack depth. No existing solution behaves like an actual company where specialized departments collaborate, disagree, negotiate, and converge on balanced decisions. Orqestra solves this by modeling an AI organization — not an AI assistant — where six Qwen-powered departments process requests end-to-end with governance, memory, and auditability.

## User Stories

### Epic: Incoming Request & Workflow Initiation

- As a business operator, I want incoming customer requests to automatically trigger a multi-department organizational workflow without me prompting any individual agent, so that Orqestra behaves like a real company making decisions, not a chatbot I have to direct.
  - [ ] A new email appearing in the monitored inbox automatically creates a Business Case
  - [ ] A manual "New Business Request" form is available as a fallback
  - [ ] The Case Card displays: Case ID, Customer Name, Request Summary, Quantity, Delivery Timeline, Status
  - [ ] A notification confirms the organization has begun processing

- As a business operator, I want Orqestra to handle ambiguous or incomplete requests gracefully, so that missing information doesn't break the workflow.
  - [ ] The Sales Agent performs intent analysis and confidence scoring on incoming requests
  - [ ] If confidence is below 70%, the case enters "Clarification Required" status
  - [ ] Missing fields are identified and displayed
  - [ ] A suggested follow-up email is generated with specific information requests
  - [ ] The operator can review, edit, send, or auto-dispatch the clarification request

- As a business operator, I want to see organizational memory being retrieved before any analysis begins, so I know the organization is operating from institutional knowledge.
  - [ ] Memory retrieval panel appears when a workflow activates
  - [ ] Retrieved entries display source category (Customer, Supplier, Historical Decision)
  - [ ] Number of memories loaded is shown per agent

### Epic: Organizational Deliberation

- As a business operator, I want each department to independently analyze a request before seeing other agents' recommendations, so that I get diverse perspectives from specialized agents.
  - [ ] Each agent performs analysis using its own Qwen API call
  - [ ] Each agent receives: case context, department objectives, relevant memory, tool outputs, organizational policies
  - [ ] Each agent produces: recommendation, confidence score, supporting evidence, risks identified, alternative options
  - [ ] The deliberation timeline streams results in real-time

- As a business operator, I want agents to be able to challenge each other's assumptions and evidence, so that the organization surfaces hidden risks.
  - [ ] Agents can issue challenges to other agents' recommendations
  - [ ] Each challenge includes: source agent, target agent, challenge type, statement, supporting evidence
  - [ ] Challenges appear as structured messages with provenance (memory, tool call, policy reference)
  - [ ] The workflow graph branches visually to show disagreement

- As a business operator, I want the Operations Manager to adjudicate conflicts using structured consensus scoring, so that the final recommendation is based on measurable trade-offs, not arbitrary authority.
  - [ ] All proposals are scored across dimensions: Customer Satisfaction, Profitability, Operational Risk, Delivery Reliability, Policy Compliance
  - [ ] Each agent contributes scores within its area of expertise
  - [ ] The Operations Manager generates a decision rationale citing evidence from all departments
  - [ ] The rationale explains not only what was chosen but why other options were rejected

### Epic: Executive Governance

- As a business operator, I want to review an Executive Decision Brief with the organization's recommendation, confidence, and consensus breakdown before taking action.
  - [ ] The brief displays: Case ID, Customer, Request Summary, Status
  - [ ] Recommended strategy with one-sentence rationale and organizational confidence score
  - [ ] Business impact: revenue estimate, profit margin, delivery confidence, risk classification
  - [ ] Consensus breakdown: each agent's position with status icon
  - [ ] Key risks section drawn from agent deliberations
  - [ ] Memory evidence section showing retrieved organizational knowledge
  - [ ] Audit indicator showing trace availability and tool call count
  - [ ] The brief answers eight questions without opening developer logs: what is recommended, why, which departments support/oppose, what risks exist, what history influenced the decision, what alternatives were considered, what actions can I take

- As a business operator, I want to Approve, Reject, or Modify constraints on a recommendation, so that I govern the organization rather than merely approving outputs.
  - [ ] Approve: accepts recommendation, advances workflow to execution
  - [ ] Reject: declines recommendation, rejection becomes a new constraint, workflow returns to deliberation
  - [ ] Modify: operator injects strategic directives (e.g., "minimum margin 20%"), agents re-deliberate under new constraints
  - [ ] Each governance iteration is numbered and auditable

### Epic: Audit & Explainability

- As a business operator, I want every decision traceable to its evidence, so that I can justify any organizational outcome.
  - [ ] Every agent action generates a structured Decision Card
  - [ ] Each Decision Card shows: recommendation, confidence, evidence, risks, memory used, tools consulted, timestamp
  - [ ] Every challenge between agents is preserved as organizational record
  - [ ] A Decision Justification Report lists: final decision, alternatives considered, reason for selection, rejected alternatives with reasons
  - [ ] Post-hoc audit trail shows full timeline of every event in the workflow

- As a business operator, I want to inspect why any agent made any decision, so that governance is transparent.
  - [ ] Clicking any department reveals: recommendation, confidence, risks, evidence, memory used, tool calls, challenges received, challenges issued
  - [ ] A visual decision graph shows the full reasoning chain from request to final outcome
  - [ ] Selecting any node in the graph reveals inputs, evidence, memory, tools used, outputs

### Epic: Organization Health Dashboard

- As a business operator, I want an Executive Overview showing how my AI organization is performing today, so that I manage the workforce like a CEO.
  - [ ] Organizational Effectiveness Score (composite of consensus rate, risk detection, policy compliance, approval success, decision confidence)
  - [ ] Cases Processed Today
  - [ ] Average Deliberation Time
  - [ ] Approval Rate
  - [ ] Escalation Rate
  - [ ] Memory Utilization Rate
  - [ ] Department Performance KPIs per agent

### Epic: Side-by-Side Benchmark

- As a judge or operator, I want to see the exact same request evaluated by a single-agent system vs. Orqestra, so that the multi-agent advantage is measurable.
  - [ ] Benchmark tab within completed workflow
  - [ ] Left panel: single-agent baseline (recommendation, confidence, risks found, factors considered, reasoning time)
  - [ ] Right panel: Orqestra result (same metrics)
  - [ ] Decision Coverage comparison (factors evaluated)
  - [ ] Risk Detection comparison (risks identified)
  - [ ] Memory Utilization comparison
  - [ ] "Why did outcomes differ?" click-through revealing what each system missed or considered

### Epic: Failure Recovery & Resilience

- As a business operator, I want the organization to degrade gracefully when agents, tools, or memory fail, so that one failure doesn't halt the entire workflow.
  - [ ] Agent timeout: workflow continues with partial information, confidence degrades, unavailable status displayed
  - [ ] Tool failure: agent produces recommendation with reduced confidence, uncertainty is surfaced
  - [ ] Memory retrieval failure: agent proceeds with confidence adjustment, zero memories returned is not a crash
  - [ ] Critical vs non-critical department failure: critical department unavailability escalates, non-critical proceeds with warning
  - [ ] Automatic retry strategy: 3 attempts (immediate, 10s, 30s), then degraded operation or escalation
  - [ ] Confidence degradation visible as failures accumulate
  - [ ] Executive escalation threshold when confidence drops below 65%
  - [ ] Organizational Completeness Score displayed during partial deliberation
  - [ ] Operations Manager failure is the only hard stop — governance unavailable, human review required

## What We're Building

All stories and acceptance criteria listed above. The MVP delivers:
- A complete order fulfillment workflow with 6 Qwen-powered agents
- Four-stage governance protocol (Independent Assessment → Cross-Agent Challenge → Consensus Scoring → Ops Manager Adjudication)
- Executive Decision Brief with Approve/Reject/Modify governance
- Organizational memory (shared + per-department) with Memory Retrieval Service
- Side-by-side benchmark against single-agent baseline
- Organization Health Dashboard with KPIs per department
- Structured hybrid communication (think in language, communicate in contracts)
- Graceful degradation for agent/tool/memory failures
- Full audit trail and explainability

## What We'd Add With More Time
- **Additional business domains** — Returns management, customer onboarding, HR operations, marketing campaigns (architecture supports it, not built)
- **Multi-tenancy** — Supporting multiple businesses with isolated data and custom workflows
- **Deep third-party integrations** — Real ERP, CRM, email, payment gateway, logistics provider connections (replaced with simulated services for MVP)
- **Autonomous execution** — Triggering real purchase orders, customer emails, and logistics bookings after human approval (human-in-the-loop only for MVP)
- **Advanced benchmarking** — Historical analytics, leaderboards, cross-workflow performance trends (single-workflow comparison only)
- **Multi-language support** — Handling requests in languages other than English
- **Notification system** — Email/Slack alerts for escalations, approvals pending, workflow completion

## Non-Goals
1. **Multi-workflow demo** — The demo shows one workflow (order fulfillment) in depth, not multiple shallow workflows.
2. **Chat interface** — Orqestra is not a conversational AI. The operator manages an organization, not a chat session.
3. **Mobile app** — Desktop/web dashboard only.
4. **Real-time streaming of every intermediate token** — The dashboard updates at milestone boundaries (recommendation complete, challenge issued, decision reached), not on every word generated.
5. **No-code agent builder** — Agent roles, tools, and policies are code-defined for the MVP.
6. **Self-hosted LLM** — All reasoning runs on Qwen Cloud APIs. No local model inference.

## Open Questions
- What is the exact Qwen model selection per agent tier? (Operational agents vs Operations Manager — to be resolved during /spec)
- What is the confidence threshold for Organizational Completeness Score? (Suggested: 80% for auto-proceed — to be finalized during /spec)
- How are the simulated business services (inventory, pricing engine, supplier DB) implemented? Mock data or lightweight microservices? (Deferred to /spec)
