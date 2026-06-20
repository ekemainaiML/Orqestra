import uuid

import pytest
from httpx import AsyncClient


class TestListCases:

    async def test_empty_returns_empty_list(self, client: AsyncClient):
        resp = await client.get("/cases")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_created_cases(self, client: AsyncClient, seed_customers, seed_case):
        resp = await client.get("/cases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["request_text"] == seed_case.request_text


class TestCreateCase:

    async def test_creates_case_successfully(self, client: AsyncClient, seed_customers):
        customer_id = str(seed_customers[0].id)
        resp = await client.post("/cases", json={
            "customer_id": customer_id,
            "request_text": "Test order — 10 units for evaluation.",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "created"
        assert data["customer_id"] == customer_id
        assert uuid.UUID(data["id"])

    async def test_rejects_nonexistent_customer(self, client: AsyncClient):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.post("/cases", json={
            "customer_id": fake_id,
            "request_text": "Test order.",
        })
        assert resp.status_code == 404

    async def test_rejects_empty_request_text(self, client: AsyncClient, seed_customers):
        resp = await client.post("/cases", json={
            "customer_id": str(seed_customers[0].id),
            "request_text": "",
        })
        assert resp.status_code == 422


class TestGetCase:

    async def test_get_existing_case(self, client: AsyncClient, seed_case):
        resp = await client.get(f"/cases/{seed_case.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(seed_case.id)
        assert "events" in data
        assert "directives" in data

    async def test_get_nonexistent_case_returns_404(self, client: AsyncClient):
        resp = await client.get(f"/cases/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_get_case_with_invalid_uuid(self, client: AsyncClient):
        resp = await client.get("/cases/not-a-uuid")
        assert resp.status_code == 422


class TestCaseGovernance:

    async def test_approve_nonexistent_case(self, client: AsyncClient):
        resp = await client.post(f"/cases/{uuid.uuid4()}/approve")
        assert resp.status_code == 400

    async def test_run_deliberation_nonexistent_case(self, client: AsyncClient):
        resp = await client.post(f"/cases/{uuid.uuid4()}/run")
        assert resp.status_code == 404


class TestReplay:

    async def test_replay_nonexistent_case(self, client: AsyncClient):
        resp = await client.get(f"/cases/{uuid.uuid4()}/replay")
        assert resp.status_code == 404

    async def test_replay_returns_state_machine(self, client: AsyncClient, seed_case):
        resp = await client.get(f"/cases/{seed_case.id}/replay")
        assert resp.status_code == 200
        data = resp.json()
        assert data["case_id"] == str(seed_case.id)
        assert "state_machine" in data
        assert data["state_machine"]["current_state"] == "created"


class TestBrief:

    async def test_brief_nonexistent_case(self, client: AsyncClient):
        resp = await client.get(f"/cases/{uuid.uuid4()}/brief")
        assert resp.status_code == 404

    async def test_brief_returns_status(self, client: AsyncClient, seed_case):
        resp = await client.get(f"/cases/{seed_case.id}/brief")
        assert resp.status_code == 200
        assert resp.json()["status"] == "created"
