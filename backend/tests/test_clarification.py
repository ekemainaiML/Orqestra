"""Unit tests for the clarification engine."""

from app.governance.clarification import compute_completeness, generate_clarification_request


def test_vague_request_needs_clarification():
    result = compute_completeness("I need stuff")
    assert result["needs_clarification"] is True
    assert result["completeness"] < 0.7
    assert result["missing_count"] > 5


def test_detailed_request_passes():
    text = (
        "I need to approve a budget of $5000 for a quantity of 100 units "
        "of inventory for the warehouse in the Chicago office region. "
        "The deadline is next Friday. This is critical for Q4 sales "
        "and the purpose is to meet quarterly targets. "
        "Reference PO ticket 2024-001."
    )
    result = compute_completeness(text)
    assert result["needs_clarification"] is False
    assert result["completeness"] >= 0.5


def test_all_fields_returned():
    result = compute_completeness("")
    assert "completeness" in result
    assert "missing_fields" in result
    assert "total_fields_checked" in result
    assert result["total_fields_checked"] == 10
    assert "missing_count" in result
    assert "needs_clarification" in result


def test_generate_clarification_request():
    comp = compute_completeness("Need supplies")
    result = generate_clarification_request("Need supplies", comp)
    assert "case_message" in result
    assert "questions" in result
    assert "missing_fields" in result
    assert "completeness_score" in result
    assert len(result["questions"]) <= 5
    assert result["completeness_score"] == comp["completeness"]


def test_amount_pattern_detected():
    result = compute_completeness("The budget is $10000")
    amount_field = next((m for m in result["missing_fields"] if m["field"] == "amount_missing"), None)
    assert amount_field is None, "Amount pattern should have been detected"


def test_timeline_pattern_detected():
    result = compute_completeness("We need this ASAP")
    field = next((m for m in result["missing_fields"] if m["field"] == "timeline_missing"), None)
    assert field is None


def test_location_pattern_detected():
    result = compute_completeness("Ship to the Chicago office")
    field = next((m for m in result["missing_fields"] if m["field"] == "location_missing"), None)
    assert field is None


def test_priority_pattern_detected():
    result = compute_completeness("This is critical")
    field = next((m for m in result["missing_fields"] if m["field"] == "priority_missing"), None)
    assert field is None
