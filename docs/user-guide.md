# Orqestra User Guide

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Dashboard](#dashboard)
4. [Creating a Case](#creating-a-case)
5. [Case Detail & Deliberation](#case-detail--deliberation)
6. [Decision Governance](#decision-governance)
7. [Audit Trail](#audit-trail)
8. [Benchmark](#benchmark)
9. [Governance Replay](#governance-replay)
10. [Demo Library](#demo-library)
11. [Admin Workflows](#admin-workflows)
12. [Integrations](#integrations)
13. [Notifications](#notifications)
14. [Multi-Tenancy](#multi-tenancy)
15. [Best Practices](#best-practices)

---

## Overview

Orqestra is an AI-powered decision-making platform where specialized agents — Sales, Finance, Inventory, Procurement, Logistics, Customer Success, Compliance — collaborate as digital departments to automate business operations. It uses a 4-stage governance protocol:

1. **Independent Assessment** — Each agent evaluates the request from its domain
2. **Challenge Round** — Agents cross-examine each other's assumptions
3. **Consensus Scoring** — Scores are computed across 5 decision dimensions
4. **Adjudication** — The Operations Manager (executive agent) synthesizes a final decision

Human operators control the approval gate: **Approve**, **Reject**, or **Modify** with strategic directives.

### Available Workflows

| Workflow | Departments | Best For |
|---|---|---|
| **Order Fulfillment** | Sales, Finance, Inventory, Procurement, Logistics, Ops Manager | Customer product orders with delivery requirements |
| **Customer Onboarding** | Customer Success, Sales, Finance, Compliance, Ops Manager | New customer KYC, credit check, compliance review |
| **Government Procurement** | Sales, Finance, Inventory, Procurement, Logistics, Compliance, Ops Manager | Public-sector RFPs, regulatory compliance, budget audits |

---

## Quick Start

1. Open Orqestra in your browser (default: `http://localhost:3000`)
2. The Dashboard loads with system metrics and the active cases table
3. Launch a **Demo Scenario** (recommended for first use) or create a **New Request**
4. During deliberation, you see live progress via Server-Sent Events
5. Once deliberation completes, **Approve**, **Reject**, or **Modify** the decision

---

## Dashboard

The Dashboard is the main landing page and provides:

**Metric Cards (top row):**
- **Cases Today** — Number of cases created today
- **Completed** — Total completed cases
- **Escalated** — Cases that escalated to deadlock
- **Avg Confidence** — Average confidence across all completed cases

**Active Cases Table:**
- Columns: Case ID, Customer, Request, Created, Workflow, Status, Confidence
- **Search bar** — Filters by text across all case fields
- **Status dropdown** — Filter by status (created, independent_assessment, approval_pending, completed, escalated, etc.)
- **Workflow dropdown** — Filter by workflow type
- Click any row to navigate to the case detail page
- Sort controls; filters debounce automatically for smooth typing

**Quick Actions (right sidebar):**
- **Launch Demo** — Opens the Demo Case Library
- **New Request** — Opens the case creation form
- **System Status** — Total events, memory retrievals, total cases

**Admin (left sidebar):**
- **Workflows** — Manage custom workflow YAML definitions
- **Validate Workflow** — Validate a workflow YAML before using

---

## Creating a Case

Navigate to **New Request** from the sidebar or dashboard.

1. **Select a Customer** — Choose from the predefined customer profiles:
   - Sarah Mitchell — Greenfield Municipal Council (government, repeat)
   - James Okafor — NovaTech Solutions (first-time, corporate)
   - Chioma Adeyemi — RenPower Africa (NGO, repeat)
   - David Chen — Sunlight Initiative (NGO, budget-constrained)

2. **Select a Workflow** — Order Fulfillment, Customer Onboarding, or Government Procurement

3. **Enter Request Details** — Describe the customer's request. Include:
   - Product/service and quantity
   - Delivery timeline
   - Budget or pricing constraints
   - Any special requirements

4. Click **Submit for Deliberation**

The system creates the case and redirects you to the case detail page.

---

## Case Detail & Deliberation

The case detail page is the control center for a single case.

### Before Running

- Case info panel shows: Created date, Confidence (once available), Event count
- **Workflow Graph** — Visual representation of departments and their order
- **Directives Panel** — Add strategic constraints before running (see Decision Governance)

### Running Deliberation

Click **Run Deliberation** (or **Continue Deliberation** if resuming).

**Live progress is displayed in real-time:**

- **Deliberation Progress Bar** — Shows which stage is active:
  - Memory (retrieving past experiences)
  - Assessment (agents evaluate independently)
  - Challenge (cross-examination round)
  - Consensus (scoring across dimensions)
  - Adjudication (executive synthesis)
  - Approval (brief generated, awaiting human decision)

- **Recent Events** — Scrollable list of latest events as they occur
- **Department Assessments** — Cards showing each agent's recommendation, confidence, reasoning, risks, and factors considered

### Deliberation Timeline

Below the assessments, the timeline shows every event in sequence:

- **Event type tags** — color-coded for quick scanning
- **Actor name** — which agent or system generated the event
- **Payload** — truncated preview of the event data
- **Tool calls** — `tool_call_executed` events show the tool name and arguments prominently

### After Deliberation

Once deliberation completes, the **Decision Board** appears with the final recommendation, and the **Approve / Reject / Modify** buttons activate.

---

## Decision Governance

When a case reaches `approval_pending` status, you have three actions:

### Approve
Accepts the Operations Manager's recommendation as final. The case moves to `completed` status and is locked.

### Reject
Rejects the decision. Optionally provide rejection feedback in the API (the system records the reason).

### Modify (Strategic Directives)

Before approving, you can inject strategic directives that change deliberation parameters:

**Available directive types:**
- **Modify Parameter** — Change a numeric value (e.g., `minimum_margin: 20`)
- **Override Threshold** — Override a decision threshold (e.g., `consensus_threshold: 0.8`)
- **Add Constraint** — Introduce a new policy constraint (e.g., `must_use_local_supplier: true`)
- **Override Decision** — Directly override a specific decision dimension

After modifying, click **Continue Deliberation** to re-run with the new constraints. The system iterates (v1, v2, v3...) and the iteration number is displayed in the case header.

### Directives Panel

The Directives panel on the case detail page lets you:
- View all active directives (type, iteration, value as JSON)
- Add new directives via the form
- Delete existing directives

Directives persist across deliberation iterations.

---

## Audit Trail

Every single event in a case's lifecycle is recorded immutably. Navigate to **Audit Trail** from the case detail page.

**Features:**
- **Grouped by iteration** — Events organized by deliberation round (v1, v2, ...)
- **Search/filter** — Filter by event type, actor, or payload content
- **Expandable details** — Click any event to see its full JSON payload
- **Event types** include: `case_created`, `memory_retrieved`, `recommendation_submitted`, `challenge_submitted`, `consensus_calculated`, `decision_generated`, `brief_presented`, `tool_call_executed`, `approval`, `rejection`, `modification`, `completed`, `escalated`, and more

Use the audit trail for compliance, debugging, or post-mortem analysis.

---

## Benchmark

The Benchmark page compares **Single-Agent** (traditional LLM) vs **Orqestra Organization** (multi-agent governance) performance on any case.

Navigate to **Benchmark** from the case detail page.

**Metrics compared:**

| Metric | Description | Higher Is |
|---|---|---|
| Decision Confidence | Overall confidence score (0–100%) | Better |
| Risks Identified | Number of distinct risks surfaced | Better |
| Factors Considered | Number of decision factors evaluated | Better |
| Reasoning Time | Processing duration in seconds | Lower is better |
| Memory Used | Organizational memory entries referenced | Better |

**Visualization:**
- Top cards show the 3 key metrics with visual bars comparing single vs organization
- Side-by-side detail panels for all 5 metrics
- Percentage improvement highlighted in green
- **Workflow Comparison** — Expand the collapsible section to compare all available workflows side-by-side (departments, agent count, model tiers)

Click **Run Benchmark** to execute both modes on the same case. Results are cached; re-run to refresh.

---

## Governance Replay

The Replay page animates the deliberation process step by step. Navigate to **Replay** from the case detail page.

**Controls:**
- **Play / Pause** — Auto-advance through steps at 1.2s intervals
- **Skip to Start / Previous / Next / Skip to End** — Manual navigation
- **Step indicator** — Visual progress bar with numbered milestones

**Steps shown:**
1. Created — Case initiated
2. Memory Retrieval — Past experiences loaded
3. Assessment — Independent agent evaluations
4. Challenge Round — Cross-examination
5. Consensus Scoring — Dimension scoring
6. Adjudication — Executive tiebreak
7. Approval — Human decision pending
8. Completed — Resolution

**Left panel:** Current step description and events at that step
**Right panel:** Detailed event log with expandable JSON payloads

Use replay for presentations, training, or understanding the deliberation flow.

---

## Demo Library

The **Demo Library** (from sidebar or dashboard Quick Actions) contains 4 pre-configured scenarios:

| Scenario | Difficulty | Agents | What It Demonstrates |
|---|---|---|---|
| **Standard Order** | Easy | 4 | Happy path, multi-agent consensus |
| **Ambiguous Request** | Medium | 5 | Handling incomplete information |
| **Department Deadlock** | Hard | 6 | Cross-agent conflict, escalation |
| **Executive Modification** | Hard | 6 | HITL constraints, re-deliberation |

Click **Launch Demo** on any scenario. The system creates the case and navigates to its detail page. Run deliberation to see the agents in action.

---

## Admin Workflows

The Admin section lets you manage custom workflow definitions.

### Workflow List
- View all built-in and custom workflows
- Each workflow shows departments, decision dimensions, policies, and consensus threshold
- Built-in workflows are marked; custom workflows are editable

### Validate Workflow
Upload or paste a workflow YAML to validate its structure before use. The validator checks:
- Department definitions (IDs, roles, model tiers)
- Objectives and policies per department
- Decision dimensions completeness
- Governance configuration (challenge round, consensus threshold, deadlock resolution)
- Policy syntax and hard constraint flags
- Approval configuration

### Workflow YAML Format
See the built-in workflows under `backend/app/workflows/` for complete examples:
- `order_fulfillment.yaml`
- `customer_onboarding.yaml`
- `government_procurement.yaml`

Each workflow defines departments, their tools, objectives, policies, decision dimensions, governance rules, and approval settings.

---

## Integrations

Orqestra connects to real enterprise systems with simulated fallbacks when API keys are not configured. All integrations include rate limiting, circuit breakers, and retry logic.

### HubSpot CRM
- **Tools:** lookup_customer, get_customer_history, get_open_opportunities, get_customer_value
- **Configure:** Set `HUBSPOT_API_KEY` in `.env`
- **Used by:** Sales agent (`customer_db` tool group)

### Odoo ERP
- **Tools:** create_rfq, create_purchase_order, check_budgets, validate_approvals, get_reorder_thresholds
- **Configure:** Set `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` in `.env`
- **Maps to Odoo models:** `purchase.requisition`, `purchase.order`, `account.budget`, `product.product`
- **Used by:** Procurement agent (`erp_service` tool group)

#### Setting Up Odoo

**Option 1 (Recommended for Development): Run Odoo Locally with Docker**

1. Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data
  odoo:
    image: odoo:18
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - odoo-data:/var/lib/odoo
volumes:
  postgres-data:
  odoo-data:
```

```bash
docker compose up -d
```

2. Open `http://localhost:8069` and create the database:

| Field | Value |
|---|---|
| Database Name | `orqestra_odoo` |
| Email | `admin@example.com` |
| Password | `StrongPassword123` |

3. Install required apps: go to **Apps** and install **Sales**, **Purchase**, and **Inventory**.

4. Create test data:
   - **Suppliers:** SolarTech Nigeria, Green Energy Solutions, BrightLight Industries
   - **Products:** 100W Solar Street Light, 200W Solar Street Light, Solar Flood Light
   - **Inventory:** e.g. 420 units of 100W Solar Street Light

5. Set user permissions: go to **Settings → Users → Admin User → Access Rights** and set Sales / Purchase / Inventory to **Administrator**.

6. Configure `.env`:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=orqestra_odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=StrongPassword123
```

7. Verify XML-RPC:

```python
import xmlrpc.client
common = xmlrpc.client.ServerProxy("http://localhost:8069/xmlrpc/2/common")
uid = common.authenticate("orqestra_odoo", "admin@example.com", "StrongPassword123", {})
print(uid)  # expected: a positive integer like 2
```

**Option 2: Use Odoo Online**

Sign up for a [free trial](https://www.odoo.com/trial), then:

```env
ODOO_URL=https://mycompany.odoo.com
ODOO_DB=mycompany
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=yourpassword
```

> Note: Trial databases may restrict certain apps or XML-RPC availability. Docker is easier for development.

**Once connected**, the Procurement agent makes real decisions:
- `check_budgets` reads from `account.budget` (planned vs actual spend)
- `get_reorder_thresholds` reads `product.product.qty_available`
- `create_rfq` creates `purchase.requisition` records
- `create_purchase_order` creates `purchase.order` records
- `validate_approvals` checks `purchase.order.state`

### Paystack (Payments)
- **Tools:** verify_payment, check_transaction_history, assess_credit_risk, recommend_payment_terms
- **Configure:** Set `PAYSTACK_SECRET_KEY` in `.env`
- **Used by:** Finance agent (`payment_service` tool group)

### DHL / GIG Logistics
- **Tools:** estimate_shipping_cost, validate_delivery_feasibility, check_shipping_routes, track_shipment
- **Configure:** Set `DHL_API_KEY` in `.env`
- **Coverage:** 9 African/international routes with 5 sample tracking records
- **Used by:** Logistics agent (`logistics_service` tool group)

### How Simulated Fallback Works
When an integration's API key is missing, Orqestra automatically returns realistic simulated data. This means:
- The platform works fully without any real API keys
- All demos and benchmarks run on simulated data
- When you add API keys, the real calls happen transparently
- No code changes needed to switch between simulated and real

### Tool Call Transparency
Every tool execution is recorded as a `tool_call_executed` event in the case timeline and audit trail. Each event shows:
- **Tool name** (e.g., `verify_payment`, `check_budgets`)
- **Arguments** passed to the tool
- **Result** returned by the tool
- **Agent** that made the call

This gives full visibility into what the AI agents are doing and what data they're using.

---

## Notifications

Orqestra can send notifications when key events occur in a case lifecycle.

### Email (SMTP)
- Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` in `.env`
- Sends email when cases are: escalated, completed, rejected, failed, approval pending, or challenged

### Slack (Webhook)
- Configure `SLACK_WEBHOOK_URL` in `.env`
- Sends messages to the configured Slack channel for the same event types

### Event Triggers
Notifications fire for: `case_escalated`, `case_completed`, `case_rejected`, `case_failed`, `approval_pending`, `challenge_issued`.

---

## Multi-Tenancy

Orqestra supports multi-tenant deployments where organizations are isolated from each other.

### How It Works
- Each tenant has a unique `slug` (e.g., `acme-corp`)
- All data tables include a `tenant_id` foreign key
- Queries are automatically filtered to the current tenant — no manual filtering needed
- Tenant context is extracted from the JWT token (auth mode) or `X-Tenant-ID` / `X-Tenant-Slug` headers (development mode)

### Tenant Management
- **Default tenant** — Seeded automatically on startup with slug `default`
- **Create tenant** — `POST /auth/tenants` with name and slug
- **List tenants** — `GET /auth/tenants`
- **Signup includes tenant** — New accounts can specify `tenant_slug`

For development, simply use the default tenant — no extra configuration needed.

---

## Best Practices

### Writing Effective Requests
- **Be specific:** Include quantities, deadlines, budgets, and constraints
- **Mention the customer:** The agents use customer history from memory
- **Specify delivery:** Logistics assessment depends on delivery location and timeline
- **Flag risks:** If you know about potential issues, mention them

### Using Directives
- Add directives **before** running deliberation to guide the outcome
- Use **Modify Parameter** for numeric trade-offs (margin vs delivery speed)
- Use **Add Constraint** for business rules (e.g., "must use preferred supplier")
- After modification, re-run deliberation to see the updated assessment

### Interpreting Results
- **Confidence > 80%** — Strong consensus; likely safe to approve
- **Confidence 50–80%** — Mixed signals; review dissenting assessments
- **Confidence < 50%** — Weak consensus; consider modifying or rejecting
- **Dissenting departments** — Flagged with a warning badge; review their reasoning
- **Tool call events** — Check which tools were called and what data they returned; ensures agents are using the right information

### Debugging with Audit Trail
- Search for specific event types to isolate issues
- Expand tool_call_executed events to see exactly what data agents received
- Compare iterations to see how directives changed outcomes
- Use the Replay page for a step-by-step walkthrough

### Performance Tips
- Benchmark new workflows before deploying them
- Use the **Validate Workflow** page to catch YAML errors early
- Review the `tool_call_executed` events to ensure agents are calling the right real integrations
- Monitor the `/health` and `/metrics` endpoints for system health

---

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Deliberation fails with "API key not configured" | `DASHSCOPE_API_KEY` not set | Add key to `.env` |
| Tool returns simulated data | Integration API key missing | Configure the respective API key |
| Frontend shows no events during deliberation | SSE connection issue | Check Redis is running |
| "max tool rounds exceeded" | Agent in infinite tool loop | Review tool definitions for the workflow |
| Dashboard metrics not loading | Backend not reachable | Check backend logs and `/health` |
| Case stuck in `approval_pending` | Waiting for human action | Approve, Reject, or Modify the case |
| Docker build fails HTTP 502/520 | Docker Hub rate limit | Wait and retry, or use a mirror registry |

---

## API Reference

For programmatic access, the REST API is documented in the README and available at `http://localhost:8000/docs` (Swagger UI).

Key endpoints:
- `GET /cases` — List/search cases with filters
- `POST /cases` — Create a case
- `POST /cases/{id}/run` — Run deliberation
- `POST /cases/{id}/approve` — Approve decision
- `POST /cases/{id}/modify` — Inject directive
- `GET /cases/{id}/audit` — Audit trail
- `GET /events/stream` — SSE live stream
- `GET /dashboard/metrics` — Dashboard KPIs
- `GET /benchmark/{id}` — Benchmark results
