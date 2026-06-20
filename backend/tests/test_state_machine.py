import pytest

from app.deliberation.state_machine import DeliberationStateMachine, StateMachineError, TERMINAL_STATES


class TestDeliberationStateMachine:

    def test_initial_state_defaults_to_created(self):
        sm = DeliberationStateMachine()
        assert sm.current_state == "created"

    def test_initial_state_custom(self):
        sm = DeliberationStateMachine("approval_pending")
        assert sm.current_state == "approval_pending"

    def test_happy_path_transitions(self):
        sm = DeliberationStateMachine()
        sequence = [
            "memory_retrieval",
            "independent_assessment",
            "challenge_round",
            "consensus_scoring",
            "adjudication",
            "approval_pending",
        ]
        for target in sequence:
            result = sm.transition(target)
            assert result == target
            assert sm.current_state == target

    def test_approval_to_completed(self):
        sm = DeliberationStateMachine("approval_pending")
        sm.transition("completed")
        assert sm.current_state == "completed"

    def test_approval_to_rejected(self):
        sm = DeliberationStateMachine("approval_pending")
        sm.transition("rejected")
        assert sm.current_state == "rejected"

    def test_modification_triggers_redeliberation(self):
        sm = DeliberationStateMachine("approval_pending")
        sm.transition("constraint_modified")
        assert sm.current_state == "constraint_modified"
        sm.transition("redeliberation_pending")
        assert sm.current_state == "redeliberation_pending"
        sm.transition("memory_retrieval")
        assert sm.current_state == "memory_retrieval"

    def test_invalid_transition_raises_error(self):
        sm = DeliberationStateMachine("created")
        with pytest.raises(StateMachineError) as exc:
            sm.transition("completed")
        assert "Cannot transition from 'created' to 'completed'" in str(exc.value)

    def test_invalid_transition_from_terminal(self):
        sm = DeliberationStateMachine("completed")
        with pytest.raises(StateMachineError):
            sm.transition("memory_retrieval")

    def test_is_terminal_true(self):
        for state in TERMINAL_STATES:
            sm = DeliberationStateMachine(state)
            assert sm.is_terminal()

    def test_is_terminal_false(self):
        non_terminal = ["created", "memory_retrieval", "independent_assessment", "approval_pending"]
        for state in non_terminal:
            sm = DeliberationStateMachine(state)
            assert not sm.is_terminal()

    def test_can_govern_only_in_approval_pending(self):
        assert DeliberationStateMachine("approval_pending").can_govern()
        assert not DeliberationStateMachine("created").can_govern()
        assert not DeliberationStateMachine("completed").can_govern()
        assert not DeliberationStateMachine("escalated").can_govern()

    def test_to_dict(self):
        sm = DeliberationStateMachine("approval_pending")
        d = sm.to_dict()
        assert d["current_state"] == "approval_pending"
        assert d["is_terminal"] is False
        assert d["can_govern"] is True

    def test_all_allowed_transitions_are_valid_states(self):
        from app.deliberation.state_machine import TRANSITIONS, STATES
        for source, targets in TRANSITIONS.items():
            assert source in STATES, f"Source state '{source}' not in STATES"
            for target in targets:
                assert target in STATES, f"Target state '{target}' not in STATES"

    def test_adjudication_escalation_path(self):
        sm = DeliberationStateMachine("adjudication")
        sm.transition("escalated")
        assert sm.current_state == "escalated"
        sm.transition("closed_without_resolution")
        assert sm.current_state == "closed_without_resolution"
        assert sm.is_terminal()

    def test_clarification_path(self):
        sm = DeliberationStateMachine("memory_retrieval")
        sm.transition("clarification_required")
        sm.transition("independent_assessment")
        assert sm.current_state == "independent_assessment"
