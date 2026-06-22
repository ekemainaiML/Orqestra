from typing import Any

STATES: list[str] = [
    "created", "memory_retrieval", "independent_assessment", "challenge_round",
    "consensus_scoring", "adjudication", "approval_pending", "clarification_required",
    "escalated", "rejected", "failed", "completed", "closed", "closed_without_resolution",
    "constraint_modified", "redeliberation_pending", "executed",
]

TERMINAL_STATES: set[str] = {"completed", "closed", "escalated", "closed_without_resolution", "rejected", "failed"}

TRANSITIONS: dict[str, list[str]] = {
    "created": ["memory_retrieval", "constraint_modified", "failed"],
    "memory_retrieval": ["independent_assessment", "clarification_required", "failed"],
    "independent_assessment": ["challenge_round", "failed"],
    "challenge_round": ["consensus_scoring", "failed"],
    "consensus_scoring": ["adjudication", "failed"],
    "adjudication": ["approval_pending", "escalated", "failed"],
    "approval_pending": ["completed", "rejected", "constraint_modified", "escalated", "failed"],
    "clarification_required": ["independent_assessment", "closed", "failed"],
    "escalated": ["closed_without_resolution", "closed"],
    "constraint_modified": ["redeliberation_pending"],
    "redeliberation_pending": ["memory_retrieval", "failed"],
    "executed": ["completed"],
}


class StateMachineError(Exception):
    pass


class DeliberationStateMachine:
    def __init__(self, current_state: str = "created"):
        self.current_state = current_state

    def transition(self, target_state: str) -> str:
        allowed = TRANSITIONS.get(self.current_state, [])
        if target_state not in allowed:
            raise StateMachineError(
                f"Cannot transition from '{self.current_state}' to '{target_state}'. "
                f"Allowed: {allowed}"
            )
        self.current_state = target_state
        return self.current_state

    def is_terminal(self) -> bool:
        return self.current_state in TERMINAL_STATES

    def can_govern(self) -> bool:
        return self.current_state == "approval_pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_state": self.current_state,
            "is_terminal": self.is_terminal(),
            "can_govern": self.can_govern(),
        }
