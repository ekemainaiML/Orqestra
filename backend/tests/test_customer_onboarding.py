from app.agents.base import MODEL_TIERS
from app.deliberation.scoring_engine import calculate_scores
from app.workflows.loader import (
    get_executive_workflow_agent,
    get_operational_workflow_agents,
    get_workflow_agent_ids,
    instantiate_agents,
    list_workflow_types,
    load_workflow_config,
)

CUSTOMER_ONBOARDING_DIMENSIONS = [
    "customer_readiness",
    "financial_viability",
    "compliance_clearance",
    "operational_capacity",
    "risk_assessment",
]

CUSTOMER_ONBOARDING_EXPERTISE = {
    "customer_success": ["customer_readiness", "operational_capacity"],
    "sales": ["customer_readiness"],
    "finance": ["financial_viability", "risk_assessment"],
    "compliance": ["compliance_clearance", "risk_assessment"],
}

CUSTOMER_ONBOARDING_KEYWORDS = {
    "customer_readiness": [
        "ready", "readiness", "onboarding", "history", "relationship",
        "qualified", "prepared", "committed", "requirements", "fit",
    ],
    "financial_viability": [
        "finance", "financial", "revenue", "profit", "margin", "payment",
        "credit", "budget", "deposit", "viable", "stable",
    ],
    "compliance_clearance": [
        "compliance", "kyc", "aml", "verified", "cleared", "approved",
        "regulatory", "certified", "passed", "sanction",
    ],
    "operational_capacity": [
        "capacity", "operational", "capability", "resource", "staff",
        "system", "infrastructure", "readiness", "support",
    ],
    "risk_assessment": [
        "risk", "exposure", "flag", "concern", "elevated", "default",
        "caution", "liability", "fraud", "threshold",
    ],
}


class TestCustomerOnboardingConfig:
    def test_workflow_type_listed(self):
        types = list_workflow_types()
        assert "customer_onboarding" in types

    def test_load_config(self):
        config = load_workflow_config("customer_onboarding")
        assert config.id == "customer_onboarding"
        assert config.name == "Customer Onboarding"
        assert len(config.departments) == 5

    def test_department_ids(self):
        config = load_workflow_config("customer_onboarding")
        ids = get_workflow_agent_ids(config)
        assert "customer_success" in ids
        assert "sales" in ids
        assert "finance" in ids
        assert "compliance" in ids
        assert "operations_manager" in ids
        assert len(ids) == 5

    def test_dimension_mappings_loaded(self):
        config = load_workflow_config("customer_onboarding")
        assert config.dimension_mappings is not None
        assert "customer_success" in config.dimension_mappings
        assert "compliance" in config.dimension_mappings
        assert config.dimension_mappings["customer_success"] == ["customer_readiness", "operational_capacity"]

    def test_decision_dimensions_loaded(self):
        config = load_workflow_config("customer_onboarding")
        assert config.decision_dimensions == CUSTOMER_ONBOARDING_DIMENSIONS

    def test_instantiate_agents(self):
        config = load_workflow_config("customer_onboarding")
        agents = instantiate_agents(config)
        assert len(agents) == 5
        role_ids = set()
        for a in agents:
            assert a.model_tier in MODEL_TIERS or a.model
            assert a.objectives
            assert a.policies
            role_ids.add(a.role.lower())
        assert "customer success" in role_ids or "customer_success" in role_ids
        assert "compliance" in role_ids

    def test_executive_agent(self):
        config = load_workflow_config("customer_onboarding")
        agent = get_executive_workflow_agent(config)
        assert "Operations Manager" in agent.role or "Manager" in agent.role

    def test_operational_agents_exclude_executive(self):
        config = load_workflow_config("customer_onboarding")
        ops = get_operational_workflow_agents(config)
        for a in ops:
            assert "Manager" not in a.role

    def test_governance_settings(self):
        config = load_workflow_config("customer_onboarding")
        assert config.governance.challenge_round is True
        assert config.governance.consensus_threshold == 0.75

    def test_policies_loaded(self):
        config = load_workflow_config("customer_onboarding")
        assert len(config.policies) == 4
        policy_ids = [p.id for p in config.policies]
        assert "kyc_clearance" in policy_ids
        assert "document_completeness" in policy_ids

    def test_approval_config(self):
        config = load_workflow_config("customer_onboarding")
        assert config.approval.required_role == "operations_manager"
        assert config.approval.auto_approve_confidence == 0.95


class TestCustomerOnboardingScoring:
    def test_financial_viability_scored(self):
        recs = [
            {"agent_id": "sales", "recommendation": "Customer is ready for onboarding. Good client history.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
            {"agent_id": "finance", "recommendation": "Revenue is strong, payment terms secured. Profit margin at 22%.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
        ]
        result = calculate_scores(
            recs,
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        assert result["overall_consensus"] > 0.0
        assert "financial_viability" in result["dimension_scores"]
        assert "customer_readiness" in result["dimension_scores"]

    def test_compliance_clearance_detected(self):
        recs = [
            {"agent_id": "compliance", "recommendation": "KYC verified, AML check passed. Compliance clearance approved.", "reasoning": "", "confidence": 0.9, "risks": [], "alternatives": []},  # noqa: E501
        ]
        result = calculate_scores(
            recs,
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        assert result["dimension_scores"].get("compliance_clearance", 0) > 0.5

    def test_risk_assessment_reflected(self):
        recs = [
            {"agent_id": "finance", "recommendation": "Client has borderline credit profile. Risk of default is elevated.", "reasoning": "", "confidence": 0.7, "risks": ["Credit risk", "Payment default risk"], "alternatives": []},  # noqa: E501
            {"agent_id": "compliance", "recommendation": "Compliance passed but some risk flags remain.", "reasoning": "", "confidence": 0.6, "risks": ["Regulatory risk"], "alternatives": []},  # noqa: E501
        ]
        result = calculate_scores(
            recs,
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        assert result["dimension_scores"].get("risk_assessment", 1.0) < 0.8

    def test_agents_only_score_their_domains(self):
        recs = [
            {"agent_id": "customer_success", "recommendation": "Good to proceed.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
            {"agent_id": "sales", "recommendation": "Proceed.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
        ]
        result = calculate_scores(
            recs,
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        for agent_id, dims in result["agent_scores"].items():
            expected = set(CUSTOMER_ONBOARDING_EXPERTISE.get(agent_id, []))
            actual = set(dims.keys())
            assert actual.issubset(expected), f"{agent_id} scored outside expertise: {actual - expected}"

    def test_all_dimensions_scored(self):
        recs = [
            {"agent_id": "customer_success", "recommendation": "Customer ready, good capacity.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
            {"agent_id": "sales", "recommendation": "Customer is a good fit.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
            {"agent_id": "finance", "recommendation": "Financial profile is strong.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
            {"agent_id": "compliance", "recommendation": "All compliance checks passed.", "reasoning": "", "confidence": 0.8, "risks": [], "alternatives": []},  # noqa: E501
        ]
        result = calculate_scores(
            recs,
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        for dim in CUSTOMER_ONBOARDING_DIMENSIONS:
            assert dim in result["dimension_scores"], f"Missing dimension: {dim}"

    def test_empty_recommendations(self):
        result = calculate_scores(
            [],
            decision_dimensions=CUSTOMER_ONBOARDING_DIMENSIONS,
            agent_expertise=CUSTOMER_ONBOARDING_EXPERTISE,
            dimension_keywords=CUSTOMER_ONBOARDING_KEYWORDS,
        )
        assert result["overall_consensus"] == 0.0
        assert result["risks"] == []
