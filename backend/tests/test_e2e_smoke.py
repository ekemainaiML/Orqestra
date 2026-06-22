"""E2E smoke test: full deliberation loop with mocked Qwen API.

Routes now use Depends(get_session), and the client fixture overrides
get_session with a test DB session. These tests verify the full
deliberation pipeline end-to-end.
"""

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
async def test_full_deliberation_loop(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "E2E test — 100 units of server equipment for data center upgrade.",
        "workflow_type": "order_fulfillment",
    })
    assert resp.status_code == 200, f"Create case failed: {resp.text}"
    case = resp.json()
    case_id = case["id"]
    assert case["status"] == "created"

    resp = await client.post(f"/cases/{case_id}/run")
    assert resp.status_code == 200, f"Run deliberation failed: {resp.text}"
    result = resp.json()
    assert result["status"] == "approval_pending"
    assert "decision" in result
    assert result["decision"]["recommendation"] == SAMPLE_RECOMMENDATION["recommendation"]

    resp = await client.get(f"/cases/{case_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["status"] == "approval_pending"
    event_types = {e["event_type"] for e in detail["events"]}
    for ev in ("memory_retrieved", "recommendation_submitted", "consensus_calculated", "decision_generated", "brief_presented"):
        assert ev in event_types, f"Missing event: {ev}"

    resp = await client.post(f"/cases/{case_id}/approve")
    assert resp.status_code == 200, f"Approve failed: {resp.text}"

    resp = await client.get(f"/cases/{case_id}")
    assert resp.status_code == 200
    final = resp.json()
    assert final["status"] == "completed"
    assert final["confidence"] == SAMPLE_RECOMMENDATION["confidence"]


@pytest.mark.asyncio
async def test_e2e_with_directives(client: AsyncClient, seed_customers):
    qwen_mod.qwen.assess_with_tools = AsyncMock(return_value=SAMPLE_RECOMMENDATION)

    customer_id = str(seed_customers[0].id)

    resp = await client.post("/cases", json={
        "customer_id": customer_id,
        "request_text": "E2E directive test — 50 laptops.",
        "workflow_type": "order_fulfillment",
    })
    case_id = resp.json()["id"]

    resp = await client.post(f"/cases/{case_id}/modify", json={"minimum_margin": "20"})
    assert resp.status_code == 200, f"Modify failed: {resp.text}"

    resp = await client.get(f"/cases/{case_id}/directives")
    assert resp.status_code == 200
    directives = resp.json()
    assert len(directives) == 1
    assert directives[0]["value"]["minimum_margin"] == "20"

    directive_id = directives[0]["id"]
    resp = await client.delete(f"/cases/{case_id}/directives/{directive_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/cases/{case_id}/directives")
    assert len(resp.json()) == 0

    resp = await client.post(f"/cases/{case_id}/run")
    assert resp.status_code == 200
    assert resp.json()["status"] == "approval_pending"
