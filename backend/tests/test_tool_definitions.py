from app.agents.base import MODEL_TIERS, resolve_model, BaseAgent
from app.agents.registry import get_agent
from app.business_tools.definitions import (
    QWEN_TOOL_DEFINITIONS,
    TOOL_EXECUTOR,
    get_tool_definitions,
    get_tool_names_for_agent,
)


class TestToolDefinitions:

    def test_all_tools_have_executors(self):
        for name in QWEN_TOOL_DEFINITIONS:
            assert name in TOOL_EXECUTOR, f"Tool '{name}' has no executor"

    def test_all_executors_have_definitions(self):
        for name in TOOL_EXECUTOR:
            assert name in QWEN_TOOL_DEFINITIONS, f"Executor '{name}' has no definition"

    def test_get_tool_names_maps_correctly(self):
        names = get_tool_names_for_agent(["pricing_engine"])
        assert "calculate_price" in names
        assert "get_exchange_rate" in names

    def test_get_tool_names_handles_empty_list(self):
        assert get_tool_names_for_agent(["customer_db"]) == []

    def test_get_tool_definitions_returns_matching(self):
        names = ["calculate_price", "check_availability"]
        defs = get_tool_definitions(names)
        assert len(defs) == 2
        assert all(d["function"]["name"] in names for d in defs)

    def test_get_tool_definitions_skips_unknown(self):
        names = ["calculate_price", "non_existent_tool"]
        defs = get_tool_definitions(names)
        assert len(defs) == 1

    def test_tool_definitions_have_valid_structure(self):
        for name, defn in QWEN_TOOL_DEFINITIONS.items():
            assert defn["type"] == "function"
            assert "name" in defn["function"]
            assert "description" in defn["function"]
            assert "parameters" in defn["function"]


class TestModelTiers:

    def test_model_tiers_defined(self):
        assert "flash" in MODEL_TIERS
        assert "operational" in MODEL_TIERS
        assert "executive" in MODEL_TIERS
        assert "max_preview" in MODEL_TIERS

    def test_resolve_model_passes_through_full_name(self):
        result = resolve_model("qwen3-custom")
        assert result == "qwen3-custom"

    def test_resolve_model_looks_up_tier(self):
        result = resolve_model("operational")
        assert result == MODEL_TIERS["operational"]

    def test_base_agent_default_tier(self):
        agent = get_agent("sales")
        assert agent.model_tier == "operational"
        assert agent.get_model() == MODEL_TIERS["operational"]

    def test_ops_manager_uses_executive_tier(self):
        agent = get_agent("operations_manager")
        assert agent.model_tier == "executive"
        assert agent.get_model() == MODEL_TIERS["executive"]

    def test_escalated_model_bumps_tier(self):
        agent = get_agent("sales")
        escalated = agent.get_escalated_model()
        assert escalated == MODEL_TIERS["executive"]

    def test_max_preview_escalation_stays_max(self):
        agent = get_agent("sales")
        agent.model_tier = "max_preview"
        escalated = agent.get_escalated_model()
        assert escalated == MODEL_TIERS["max_preview"]


class TestToolExecution:

    async def test_calculate_price(self):
        result = await TOOL_EXECUTOR["calculate_price"](quantity=100)
        assert result["quantity"] == 100
        assert result["unit_price"] > 0
        assert result["subtotal"] > 0

    async def test_calculate_price_with_volume_discount(self):
        result = await TOOL_EXECUTOR["calculate_price"](quantity=500)
        assert result["volume_discount_applied"] is True

    async def test_check_availability(self):
        result = await TOOL_EXECUTOR["check_availability"](
            product="solar_street_light_60w", quantity=100
        )
        assert result["product"] == "solar_street_light_60w"
        assert "available" in result
        assert "shortfall" in result

    async def test_find_suppliers(self):
        result = await TOOL_EXECUTOR["find_suppliers"](region="Asia")
        assert len(result) > 0
        assert all(s["region"] == "Asia" for s in result)

    async def test_check_policy(self):
        result = await TOOL_EXECUTOR["check_policy"](
            policy_id="minimum_margin",
            context={"margin_pct": 18.5},
        )
        assert result["policy_id"] == "minimum_margin"
        assert "compliant" in result

    async def test_get_all_policies(self):
        result = await TOOL_EXECUTOR["get_all_policies"]()
        assert len(result) > 0
        assert all("id" in p for p in result)

    async def test_get_supplier(self):
        result = await TOOL_EXECUTOR["get_supplier"](
            supplier_id="b2c3d4e5-0001-4000-8000-000000000001"
        )
        assert result is not None
        assert result["name"] == "SolarTech Manufacturing"


class TestAgentTools:

    def test_sales_agent_has_pricing_tools(self):
        agent = get_agent("sales")
        tools = agent.get_qwen_tools()
        names = [t["function"]["name"] for t in tools]
        assert "calculate_price" in names
        assert "get_exchange_rate" in names

    def test_inventory_agent_has_inventory_tools(self):
        agent = get_agent("inventory")
        tools = agent.get_qwen_tools()
        names = [t["function"]["name"] for t in tools]
        assert "check_availability" in names
        assert "get_product_specs" in names

    def test_procurement_agent_has_supplier_tools(self):
        agent = get_agent("procurement")
        tools = agent.get_qwen_tools()
        names = [t["function"]["name"] for t in tools]
        assert "find_suppliers" in names
        assert "get_supplier" in names

    def test_ops_manager_has_policy_tools(self):
        agent = get_agent("operations_manager")
        tools = agent.get_qwen_tools()
        names = [t["function"]["name"] for t in tools]
        assert "check_policy" in names
        assert "get_all_policies" in names

    def test_system_prompt_mentions_tools(self):
        agent = get_agent("finance")
        prompt = agent._build_system_prompt()
        assert "calculate_price" in prompt
        assert "get_exchange_rate" in prompt
        assert "check_policy" in prompt

    def test_agent_with_no_tools_still_works(self):
        class NoToolAgent(BaseAgent):
            role = "Test"
            tools = []
            model_tier = "operational"

            async def assess(self, context):
                pass

        agent = NoToolAgent()
        assert agent.get_qwen_tools() == []
        prompt = agent._build_system_prompt()
        assert "calculate_price" not in prompt
        assert "check_availability" not in prompt


class TestTierEscalation:

    def test_escalate_tier_chain(self):
        from app.deliberation.agent_manager import escalate_tier, TIER_ORDER

        assert escalate_tier("flash") == "operational"
        assert escalate_tier("operational") == "executive"
        assert escalate_tier("executive") == "max_preview"
        assert escalate_tier("max_preview") == "max_preview"

    def test_override_tier_changes_model(self):
        agent = get_agent("sales")
        original = agent.get_model()

        agent.model_tier = "executive"
        escalated = agent.get_model()

        assert escalated != original
        assert escalated == MODEL_TIERS["executive"]
