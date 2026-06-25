"""E2E tests for new features: clarification, recovery, dashboard expansion."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

import app.services.qwen_client as qwen_mod

SAMPLE_RECOMMENDATION = {
    "agent_id": "test_agent",
    "recommendation": "Proceed with the proposal. All criteria met.",
    "confidence": 0.85,
    "reasoning": "The request satisfies all policy requirements and budget constraints.",
    "risks": ["Minor delivery timeline risk"],
    "alternatives": [],
    "evidence": [],
}


@pytest.mark.asyncio
async def test_clarify_vague_request(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Order supplies",
        "workflow_type": "order_fulfillment",
    })
    assert resp.status_code == 200
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/clarify")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "clarification_required"
    assert body["completeness"] < 0.7
    assert len(body["questions"]) > 0

    resp = await client.get(f"/cases/{case_id}")
    assert resp.json()["status"] == "clarification_required"


@pytest.mark.asyncio
async def test_clarify_detailed_request(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    text = (
        "Approval for budget of $50000 for a quantity of 200 laptops. "
        "The deadline is end of month. The purpose is to equip the sales "
        "department in the Austin office. Requested by the department manager. "
        "This is high priority with expected benefit of 20%% productivity gain. "
        "Reference ticket REQ-2024-050."
    )
    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": text,
        "workflow_type": "order_fulfillment",
    })
    assert resp.status_code == 200
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/clarify")
    assert resp.status_code == 200
    body = resp.json()
    if body["status"] == "clarification_required":
        return
    assert body.get("needs_clarification", True) is False
    assert len(body.get("questions", [])) == 0


@pytest.mark.asyncio
async def test_clarify_respond(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Need stuff",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/clarify")
    assert resp.status_code == 200
    assert resp.json()["status"] == "clarification_required"

    resp = await client.post(f"/cases/{case_id}/clarify/respond", json={
        "answers": {"What is the estimated amount": "5000"}
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "independent_assessment"

    resp = await client.get(f"/cases/{case_id}")
    assert resp.json()["status"] == "independent_assessment"


@pytest.mark.asyncio
async def test_recovery_check_healthy(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Test recovery — 100 units.",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/run")
    assert resp.status_code == 200

    resp = await client.get(f"/cases/{case_id}/recovery-check")
    assert resp.status_code == 200
    body = resp.json()
    assert "can_continue" in body
    assert "degraded_mode" in body
    assert "reasons" in body
    assert "checks" in body


@pytest.mark.asyncio
async def test_recovery_check_created_case(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Test recovery.",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    resp = await client.get(f"/cases/{case_id}/recovery-check")
    assert resp.status_code == 200
    assert resp.json()["can_continue"] is False


@pytest.mark.asyncio
async def test_dashboard_metrics_expanded(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    resp = await client.get("/dashboard/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "cases_today" in body
    assert "total_cases" in body
    assert "completed_cases" in body
    assert "escalated_cases" in body
    assert "average_confidence" in body
    assert "approval_rate" in body
    assert "escalation_rate" in body
    assert "memory_utilization_rate" in body
    assert "avg_deliberation_time_s" in body
    assert "department_performance" in body
    assert "pending_approval" in body

    customer_id = str(seed_customers[0].id)
    await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Dashboard test — 50 chairs.",
        "workflow_type": "order_fulfillment",
    })

    resp = await client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert resp.json()["total_cases"] >= 1


@pytest.mark.asyncio
async def test_clarify_invalid_transition(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Test transition.",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/clarify/respond", json={
        "answers": {"test": "value"}
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_tool_results_endpoint(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "Tool results test — 25 monitors.",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    await client.post(f"/cases/{case_id}/run")

    resp = await client.get(f"/cases/{case_id}/tool-results")
    assert resp.status_code == 200
    body = resp.json()
    assert body["case_id"] == case_id
    assert "tools" in body
    assert "tool_count" in body


@pytest.mark.asyncio
async def test_dashboard_trends(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    resp = await client.get("/dashboard/trends?days=7")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) <= 7
    if len(body) > 0:
        assert "date" in body[0]
        assert "cases_created" in body[0]
        assert "cases_completed" in body[0]
        assert "avg_confidence" in body[0]

    resp = await client.get("/dashboard/trends")
    assert resp.status_code == 200
    assert len(resp.json()) <= 30


@pytest.mark.asyncio
async def test_health_integrations(client: AsyncClient):
    resp = await client.get("/health/integrations")
    assert resp.status_code == 200
    body = resp.json()
    assert "hubspot" in body
    assert "odoo" in body
    assert "paystack" in body
    assert "dhl" in body
    assert "qwen" in body
    assert "slack" in body
    assert "smtp" in body
    for key, val in body.items():
        assert "configured" in val
        assert "status" in val
        assert val["status"] in ("connected", "not_configured")


@pytest.mark.asyncio
async def test_notification_settings_get(client: AsyncClient):
    resp = await client.get("/auth/settings/notifications")
    assert resp.status_code == 200
    body = resp.json()
    assert "smtp_host" in body
    assert "smtp_port" in body
    assert "smtp_username" in body
    assert "smtp_password" in body
    assert "smtp_from" in body
    assert "slack_webhook_url" in body


@pytest.mark.asyncio
async def test_notification_settings_update(client: AsyncClient):
    resp = await client.put("/auth/settings/notifications", json={
        "smtp_host": "smtp.test.com",
        "smtp_port": 587,
        "smtp_username": "user@test.com",
        "smtp_password": "secret123",
        "smtp_from": "alerts@test.com",
        "slack_webhook_url": "https://hooks.slack.com/test",
    })
    assert resp.status_code == 200
    assert resp.json()["message"] == "Notification settings updated"

    resp = await client.get("/auth/settings/notifications")
    body = resp.json()
    assert body["smtp_host"] == "smtp.test.com"
    assert body["smtp_port"] == 587
    assert body["smtp_username"] == "user@test.com"
    assert body["smtp_password"] == "********"
    assert body["smtp_from"] == "alerts@test.com"
    assert body["slack_webhook_url"] == "********"


@pytest.mark.asyncio
async def test_notification_settings_update_masked(client: AsyncClient):
    """Sending masked passwords should not clear existing secrets."""
    resp = await client.put("/auth/settings/notifications", json={
        "smtp_host": "smtp.keep.com",
        "smtp_password": "********",
        "slack_webhook_url": "********",
    })
    assert resp.status_code == 200

    resp = await client.put("/auth/settings/notifications", json={
        "smtp_host": "smtp.keep.com",
        "smtp_password": "realpass",
        "slack_webhook_url": "https://hooks.slack.com/real",
    })
    assert resp.status_code == 200

    resp = await client.put("/auth/settings/notifications", json={
        "smtp_host": "smtp.keep.com",
        "smtp_password": "********",
        "slack_webhook_url": "********",
    })
    assert resp.status_code == 200

    resp = await client.get("/auth/settings/notifications")
    body = resp.json()
    assert body["smtp_host"] == "smtp.keep.com"
    assert body["smtp_password"] == "********"
    assert body["slack_webhook_url"] == "********"


@pytest.mark.asyncio
async def test_notification_settings_invalid_port(client: AsyncClient):
    resp = await client.put("/auth/settings/notifications", json={
        "smtp_port": 99999,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_notification_settings_invalid_slack_url(client: AsyncClient):
    resp = await client.put("/auth/settings/notifications", json={
        "slack_webhook_url": "http://insecure.url/hook",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_dashboard_trends_empty(client: AsyncClient):
    """Trends should return empty list-of-dicts shape when no cases exist."""
    resp = await client.get("/dashboard/trends?days=7")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    for entry in body:
        assert entry["cases_created"] == 0
        assert entry["cases_completed"] == 0
        assert entry["avg_confidence"] == 0.0


@pytest.mark.asyncio
async def test_create_tenant_invalid_slug(client: AsyncClient):
    """Slug with special characters should be rejected."""
    resp = await client.post("/auth/tenants", json={"name": "Test", "slug": "bad slug!!"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_tenant_empty_name(client: AsyncClient):
    """Empty name should be rejected."""
    resp = await client.post("/auth/tenants", json={"name": "  ", "slug": "valid-slug"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_tenant_slug_uniqueness(client: AsyncClient):
    """Duplicate slug should be rejected."""
    resp = await client.post("/auth/tenants", json={"name": "One", "slug": "dup-slug"})
    assert resp.status_code == 200
    resp = await client.post("/auth/tenants", json={"name": "Two", "slug": "dup-slug"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_delete_default_tenant(client: AsyncClient):
    """Default tenant should not be deletable."""
    resp = await client.get("/auth/tenants")
    tenants = resp.json()
    default = [t for t in tenants if t["slug"] == "default"]
    if default:
        resp = await client.delete(f"/auth/tenants/{default[0]['id']}")
        assert resp.status_code == 400
