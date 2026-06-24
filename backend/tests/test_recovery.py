"""Unit tests for the recovery policy engine."""

from app.governance.recovery import (
    CRITICAL_DEPARTMENTS,
    MIN_COMPLETENESS_THRESHOLD,
    MIN_CONFIDENCE_THRESHOLD,
    PolicyEngine,
)


def test_healthy_case():
    engine = PolicyEngine()
    result = engine.can_continue(
        {"completeness": 0.9, "confidence": 0.85, "status": "approval_pending"},
        {"recommendations": [
            {"agent_id": "finance", "confidence": 0.9},
            {"agent_id": "legal", "confidence": 0.8},
        ]},
    )
    assert result["can_continue"] is True
    assert result["degraded_mode"] is False
    assert len(result["reasons"]) == 0


def test_low_completeness():
    engine = PolicyEngine()
    result = engine.can_continue(
        {"completeness": 0.1, "confidence": 0.85, "status": "independent_assessment"},
        {"recommendations": []},
    )
    assert result["can_continue"] is False
    assert any("Completeness" in r for r in result["reasons"])


def test_low_confidence():
    engine = PolicyEngine()
    result = engine.can_continue(
        {"completeness": 0.9, "confidence": 0.05, "status": "approval_pending"},
        {"recommendations": []},
    )
    assert result["can_continue"] is False
    assert any("Confidence" in r for r in result["reasons"])


def test_critical_department_failure():
    engine = PolicyEngine()
    result = engine.can_continue(
        {"completeness": 0.9, "confidence": 0.85, "status": "approval_pending"},
        {"recommendations": [
            {"agent_id": "finance", "confidence": 0.05},
            {"agent_id": "legal", "confidence": 0.9},
        ]},
    )
    assert result["can_continue"] is False
    assert any("critical" in r for r in result["reasons"])


def test_all_critical_departments_fail():
    engine = PolicyEngine()
    recs = [{"agent_id": dept, "confidence": 0.05} for dept in CRITICAL_DEPARTMENTS]
    result = engine.can_continue(
        {"completeness": 0.9, "confidence": 0.85, "status": "approval_pending"},
        {"recommendations": recs},
    )
    assert result["can_continue"] is False


def test_non_critical_failure_tolerated():
    engine = PolicyEngine()
    recs = [
        {"agent_id": "finance", "confidence": 0.9},
        {"agent_id": "procurement", "confidence": 0.05},
        {"agent_id": "logistics", "confidence": 0.05},
    ]
    result = engine.can_continue(
        {"completeness": 0.9, "confidence": 0.85, "status": "approval_pending"},
        {"recommendations": recs},
    )
    assert result["can_continue"] is True


def test_empty_case():
    engine = PolicyEngine()
    result = engine.can_continue(
        {"completeness": 0.0, "confidence": 0.0, "status": "created"},
        {"recommendations": []},
    )
    assert result["can_continue"] is False
    assert len(result["reasons"]) >= 2


def test_thresholds_constant():
    assert MIN_COMPLETENESS_THRESHOLD == 0.40
    assert MIN_CONFIDENCE_THRESHOLD == 0.30
    assert "finance" in CRITICAL_DEPARTMENTS
    assert "legal" in CRITICAL_DEPARTMENTS
