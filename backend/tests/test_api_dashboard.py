from httpx import AsyncClient


class TestDashboard:

    async def test_metrics_return_defaults_when_no_data(self, client: AsyncClient):
        resp = await client.get("/dashboard/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "cases_today" in data
        assert "total_cases" in data
        assert "completed_cases" in data
        assert "average_confidence" in data
        assert "total_events" in data

    async def test_metrics_after_creating_case(self, client: AsyncClient, seed_customers):
        await client.post("/cases", json={
            "customer_id": str(seed_customers[0].id),
            "request_text": "Test order.",
        })
        resp = await client.get("/dashboard/metrics")
        data = resp.json()
        assert data["total_cases"] >= 1
