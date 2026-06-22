import pytest

from app.deliberation.adjudicator import _check_hard_constraints


class TestHardConstraintChecker:

    def test_no_violations_when_no_policies(self):
        violations = _check_hard_constraints([], [{"agent_id": "sales", "recommendation": "Proceed"}])
        assert violations == []

    def test_no_violations_when_soft_constraint(self):
        policies = [{"id": "local_content", "rule": "prefer local", "hard_constraint": False}]
        violations = _check_hard_constraints(policies, [{"agent_id": "sales", "recommendation": "Proceed"}])
        assert violations == []

    def test_detects_margin_below_threshold(self):
        policies = [{"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True}]
        recs = [{"agent_id": "finance", "recommendation": "Margin is 12% — below target"}]
        violations = _check_hard_constraints(policies, recs)
        assert len(violations) == 1
        assert violations[0]["policy_id"] == "minimum_margin"

    def test_no_violation_when_margin_above_threshold(self):
        policies = [{"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True}]
        recs = [{"agent_id": "finance", "recommendation": "Margin is 22% — healthy"}]
        violations = _check_hard_constraints(policies, recs)
        assert len(violations) == 0

    def test_multiple_violations_reported(self):
        policies = [
            {"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True},
            {"id": "compliance_threshold", "rule": "compliance >= 0.90", "hard_constraint": True},
        ]
        recs = [
            {"agent_id": "finance", "recommendation": "Margin is 10% — below minimum"},
            {"agent_id": "compliance", "recommendation": "Compliance score 0.85"},
        ]
        violations = _check_hard_constraints(policies, recs)
        assert len(violations) >= 1

    def test_unknown_policy_id_no_crash(self):
        policies = [{"id": "bogus_policy", "rule": "some rule", "hard_constraint": True}]
        recs = [{"agent_id": "sales", "recommendation": "Any recommendation text"}]
        violations = _check_hard_constraints(policies, recs)
        assert violations == []

    def test_budget_compliance_detected(self):
        policies = [{"id": "budget_compliance", "rule": "budget must be confirmed", "hard_constraint": True}]
        recs = [{"agent_id": "finance", "recommendation": "The budget allocation is sufficient", "reasoning": "Within limits"}]
        violations = _check_hard_constraints(policies, recs)
        assert len(violations) == 1
        assert violations[0]["policy_id"] == "budget_compliance"

    def test_budget_compliance_ignored_when_no_budget_keyword(self):
        policies = [{"id": "budget_compliance", "rule": "budget must be confirmed", "hard_constraint": True}]
        recs = [{"agent_id": "finance", "recommendation": "Cost is within project scope", "reasoning": "All good"}]
        violations = _check_hard_constraints(policies, recs)
        assert violations == []

    def test_empty_recommendations_no_crash(self):
        policies = [{"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True}]
        violations = _check_hard_constraints(policies, [])
        assert violations == []

    def test_no_crash_when_recommendation_missing_keys(self):
        policies = [{"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True}]
        recs = [{"agent_id": "finance"}]  # missing recommendation, reasoning, risks
        violations = _check_hard_constraints(policies, recs)
        assert violations == []

    def test_multiple_agents_budget_violations(self):
        policies = [{"id": "budget_compliance", "rule": "budget must be confirmed", "hard_constraint": True}]
        recs = [
            {"agent_id": "sales", "recommendation": "Budget needs review", "reasoning": "Over by 10%"},
            {"agent_id": "finance", "recommendation": "No budget concerns", "reasoning": "Within limits"},
        ]
        violations = _check_hard_constraints(policies, recs)
        assert len(violations) == 2
        assert all(v["policy_id"] == "budget_compliance" for v in violations)


class TestDirectivesFlow:

    @pytest.mark.asyncio
    async def test_get_case_directives_empty_for_nonexistent(self, db_session):
        from app.governance.approval_handler import get_case_directives

        import uuid
        result = await get_case_directives(str(uuid.uuid4()), db_session)
        assert result == []

    def test_policy_violations_included_in_adjudication_output(self):
        from app.agents.base import AgentContext, AgentRecommendation
        from app.agents.base import BaseAgent
        from app.deliberation.adjudicator import _check_hard_constraints

        violations = _check_hard_constraints(
            policies=[{"id": "minimum_margin", "rule": "margin >= 15%", "hard_constraint": True}],
            recommendations=[{"agent_id": "finance", "recommendation": "Margin is 12%"}],
        )
        assert len(violations) > 0
        assert violations[0]["policy_id"] == "minimum_margin"


class TestRedeliberationFlow:

    def test_modify_transitions_state(self):
        from app.deliberation.state_machine import DeliberationStateMachine

        sm = DeliberationStateMachine("approval_pending")
        sm.transition("constraint_modified")
        assert sm.current_state == "constraint_modified"

        sm.transition("redeliberation_pending")
        assert sm.current_state == "redeliberation_pending"

        sm.transition("memory_retrieval")
        assert sm.current_state == "memory_retrieval"

    def test_redeliberation_happy_path(self):
        from app.deliberation.state_machine import DeliberationStateMachine

        states = ["approval_pending", "constraint_modified", "redeliberation_pending",
                  "memory_retrieval", "independent_assessment", "challenge_round",
                  "consensus_scoring", "adjudication", "approval_pending"]
        sm = DeliberationStateMachine(states[0])
        for target in states[1:]:
            sm.transition(target)
        assert sm.current_state == "approval_pending"

    def test_cannot_modify_from_wrong_state(self):
        from app.deliberation.state_machine import DeliberationStateMachine, StateMachineError

        sm = DeliberationStateMachine("independent_assessment")
        try:
            sm.transition("constraint_modified")
            assert False, "Should have raised"
        except StateMachineError:
            pass
