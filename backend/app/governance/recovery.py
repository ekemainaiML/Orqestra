from typing import Any

MIN_COMPLETENESS_THRESHOLD = 0.40
MIN_CONFIDENCE_THRESHOLD = 0.30
CRITICAL_DEPARTMENTS: set[str] = {"finance", "legal", "compliance", "operations_manager", "risk_management"}


class PolicyEngine:
    def can_continue(self, case: dict[str, Any], assessment: dict[str, Any]) -> dict[str, Any]:
        completeness = case.get("completeness") or 0.0
        confidence = case.get("confidence") or 0.0

        recommendations = assessment.get("recommendations", [])

        critical_agents = [r for r in recommendations
                           if r.get("agent_id", "") in CRITICAL_DEPARTMENTS]
        non_critical_agents = [r for r in recommendations
                               if r.get("agent_id", "") not in CRITICAL_DEPARTMENTS]

        critical_failures = sum(
            1 for r in critical_agents if (r.get("confidence") or 0) < MIN_CONFIDENCE_THRESHOLD
        )
        non_critical_failures = sum(
            1 for r in non_critical_agents if (r.get("confidence") or 0) < MIN_CONFIDENCE_THRESHOLD
        )

        completeness_pass = completeness >= MIN_COMPLETENESS_THRESHOLD
        confidence_pass = confidence >= MIN_CONFIDENCE_THRESHOLD
        critical_pass = len(critical_agents) > 0 and critical_failures == 0
        non_critical_tolerance = non_critical_failures <= max(1, len(non_critical_agents) // 2)

        can_proceed = completeness_pass and confidence_pass and (len(critical_agents) == 0 or critical_pass)

        if can_proceed and not non_critical_tolerance:
            can_proceed = True

        degraded = bool(
            (not completeness_pass or not confidence_pass or not critical_pass)
            and can_proceed
        )

        reasons: list[str] = []
        if not completeness_pass:
            reasons.append(f"Completeness ({completeness:.2f}) below threshold ({MIN_COMPLETENESS_THRESHOLD})")
        if not confidence_pass:
            reasons.append(f"Confidence ({confidence:.2f}) below threshold ({MIN_CONFIDENCE_THRESHOLD})")
        if not critical_pass:
            reasons.append(f"{critical_failures} critical department(s) below confidence threshold")
        if not non_critical_tolerance:
            reasons.append(f"{non_critical_failures} non-critical department(s) below confidence threshold")

        return {
            "can_continue": can_proceed,
            "degraded_mode": degraded,
            "reasons": reasons,
            "checks": {
                "completeness_pass": completeness_pass,
                "confidence_pass": confidence_pass,
                "critical_pass": critical_pass,
                "non_critical_tolerance": non_critical_tolerance,
            },
            "thresholds": {
                "min_completeness": MIN_COMPLETENESS_THRESHOLD,
                "min_confidence": MIN_CONFIDENCE_THRESHOLD,
                "critical_departments": list(CRITICAL_DEPARTMENTS),
            },
        }
