from typing import Any

from app.events.publisher import publish_event

MAX_ITERATIONS_BEFORE_WARNING = 3


async def start_iteration(case_id: str, iteration_number: int) -> dict[str, Any]:
    await publish_event(case_id, "iteration_started", "system", {
        "iteration": iteration_number,
        "is_warning": iteration_number >= MAX_ITERATIONS_BEFORE_WARNING,
    })

    return {
        "iteration": iteration_number,
        "warning": iteration_number >= MAX_ITERATIONS_BEFORE_WARNING,
        "message": (
            f"Governance iteration {iteration_number} started. "
            f"This iteration {'exceeds' if iteration_number >= MAX_ITERATIONS_BEFORE_WARNING else 'is within'} "
            f"the recommended limit of {MAX_ITERATIONS_BEFORE_WARNING}."
        ) if iteration_number >= MAX_ITERATIONS_BEFORE_WARNING else f"Iteration {iteration_number} started.",
    }


async def get_iteration_history(case_id: str, current_iteration: int) -> list[dict[str, Any]]:
    iterations = []
    for i in range(current_iteration + 1):
        iterations.append({
            "iteration": i,
            "status": "active" if i == current_iteration else "completed",
            "governance_action": "modify" if i > 0 else "initial",
        })
    return iterations
