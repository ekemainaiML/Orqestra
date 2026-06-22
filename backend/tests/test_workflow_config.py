from app.workflows.loader import (
    get_executive_workflow_agent,
    get_operational_workflow_agents,
    get_workflow_agent_ids,
    list_workflow_types,
    load_workflow_config,
    instantiate_agents,
)
from app.agents.base import MODEL_TIERS


class TestWorkflowConfigLoader:

    def test_list_workflow_types(self):
        types = list_workflow_types()
        assert "order_fulfillment" in types
        assert "government_procurement" in types

    def test_load_order_fulfillment(self):
        config = load_workflow_config("order_fulfillment")
        assert config.id == "order_fulfillment"
        assert config.name == "Order Fulfillment"
        assert len(config.departments) == 6

    def test_load_government_procurement(self):
        config = load_workflow_config("government_procurement")
        assert config.id == "government_procurement"
        assert config.name == "Government Procurement Review"
        assert len(config.departments) == 6

    def test_unknown_workflow_raises(self):
        try:
            load_workflow_config("nonexistent_workflow")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Unknown workflow type" in str(e)

    def test_get_workflow_agent_ids(self):
        config = load_workflow_config("order_fulfillment")
        ids = get_workflow_agent_ids(config)
        assert "sales" in ids
        assert "inventory" in ids
        assert "finance" in ids
        assert "procurement" in ids
        assert "logistics" in ids
        assert "operations_manager" in ids
        assert len(ids) == 6

    def test_government_procurement_agent_ids(self):
        config = load_workflow_config("government_procurement")
        ids = get_workflow_agent_ids(config)
        assert "procurement_review" in ids
        assert "technical_evaluation" in ids
        assert "finance" in ids
        assert "compliance" in ids
        assert "legal" in ids
        assert "procurement_director" in ids
        assert len(ids) == 6

    def test_instantiate_agents(self):
        config = load_workflow_config("order_fulfillment")
        agents = instantiate_agents(config)
        assert len(agents) == 6
        role_ids = set()
        for a in agents:
            assert a.model_tier in MODEL_TIERS or a.model
            assert a.objectives
            assert a.policies
            role_ids.add(a.role.lower())
        assert any("sales" in r for r in role_ids)
        assert any("finance" in r for r in role_ids)

    def test_get_executive_agent(self):
        config = load_workflow_config("order_fulfillment")
        agent = get_executive_workflow_agent(config)
        assert agent.role == "Operations Manager"
        assert agent.model_tier in ("executive", "max_preview")

    def test_get_executive_agent_procurement(self):
        config = load_workflow_config("government_procurement")
        agent = get_executive_workflow_agent(config)
        assert "Director" in agent.role
        assert agent.model_tier in ("executive", "max_preview")

    def test_operational_agents_exclude_executive(self):
        config = load_workflow_config("order_fulfillment")
        ops = get_operational_workflow_agents(config)
        for a in ops:
            assert "Manager" not in a.role
            assert "Director" not in a.role

    def test_agent_objectives_flow_from_config(self):
        config = load_workflow_config("order_fulfillment")
        agents = instantiate_agents(config)
        for a in agents:
            assert len(a.objectives) > 0
            assert len(a.policies) > 0

    def test_workflow_departments_have_roles(self):
        config = load_workflow_config("order_fulfillment")
        for dept in config.departments:
            assert dept.role
            assert len(dept.role) >= 5

    def test_governance_settings_loaded(self):
        config = load_workflow_config("order_fulfillment")
        assert config.governance.challenge_round is True
        assert config.governance.consensus_threshold == 0.75

    def test_procurement_governance_settings(self):
        config = load_workflow_config("government_procurement")
        assert config.governance.consensus_threshold == 0.80
        assert config.governance.deadlock_resolution == "escalate"

    def test_model_dump_flat(self):
        config = load_workflow_config("order_fulfillment")
        flat = config.model_dump_flat()
        assert flat["id"] == "order_fulfillment"
        assert "departments" in flat
        assert "decision_dimensions" in flat
        assert "policies" in flat
        assert flat["required_role"] == "operations_manager"
