from httpx import AsyncClient


class TestDemoCases:

    async def test_list_demo_cases_returns_four(self, client: AsyncClient):
        resp = await client.get("/demo/cases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4

    async def test_each_demo_has_required_fields(self, client: AsyncClient):
        resp = await client.get("/demo/cases")
        data = resp.json()
        for scenario in data:
            assert "id" in scenario
            assert "name" in scenario
            assert "customer_id" in scenario
            assert "request_text" in scenario
            assert "difficulty" in scenario
            assert "agent_count" in scenario
