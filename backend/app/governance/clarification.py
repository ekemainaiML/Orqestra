import re
from typing import Any

CLARIFICATION_PATTERNS: list[tuple[str, str, str]] = [  # noqa: E501
    ("amount_missing", r"(?i)how\s+much|budget|amount|cost|price|pricing|fee",
     "What is the estimated amount or budget for this request?"),
    ("timeline_missing", r"(?i)when|deadline|timeline|urgency|asap|rush|timeframe",
     "What is the expected timeline or deadline?"),
    ("quantity_missing", r"(?i)how\s+many|quantity|count|number\s+of|volume",
     "What quantity or count is involved?"),
    ("reason_missing", r"(?i)why|reason|justification|purpose|objective|goal",
     "What is the business justification or objective?"),
    ("location_missing", r"(?i)where|location|region|address|site|office",
     "Which location or region does this apply to?"),
    ("stakeholder_missing", r"(?i)who|stakeholder|approver|manager|owner|responsible",
     "Who are the key stakeholders or decision-makers?"),
    ("priority_missing", r"(?i)priority|critical|important|high\s+priority|low\s+priority",
     "What is the priority level of this request?"),
    ("impact_missing", r"(?i)impact|effect|consequence|outcome|benefit|risk",
     "What is the expected business impact or benefit?"),
    ("department_missing", r"(?i)department|team|division|unit|group",
     "Which department or team does this concern?"),
    ("reference_missing", r"(?i)reference|ticket|order\s*id|case\s*id|po\s*number|invoice",
     "Is there a reference number, PO, or ticket ID?"),
]


MIN_CONFIDENCE_FOR_CLARIFICATION = 0.70


def compute_completeness(request_text: str) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for field_id, pattern, question in CLARIFICATION_PATTERNS:
        if not re.search(pattern, request_text):
            missing.append({"field": field_id, "question": question})

    word_count = len(request_text.split())
    has_numbers = bool(re.search(r"\d+", request_text))
    has_named_entity = bool(re.search(r"(?i)\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", request_text))

    signal_score = min(1.0, word_count / 80) * 0.4
    signal_score += 0.3 if has_numbers else 0.0
    signal_score += 0.3 if has_named_entity else 0.0

    coverage = 1.0 - (len(missing) / len(CLARIFICATION_PATTERNS))
    completeness = min(1.0, (signal_score + coverage) / 2)

    return {
        "completeness": round(completeness, 4),
        "missing_fields": missing,
        "total_fields_checked": len(CLARIFICATION_PATTERNS),
        "missing_count": len(missing),
        "needs_clarification": completeness < MIN_CONFIDENCE_FOR_CLARIFICATION,
    }


def generate_clarification_request(request_text: str, completeness_result: dict[str, Any]) -> dict[str, Any]:
    questions = [m["question"] for m in completeness_result["missing_fields"]]

    message_parts = [
        "Your request needs additional information before it can be processed.",
        "",
    ]

    if questions:
        message_parts.append("Please provide the following details:")
        message_parts.extend(f"- {q}" for q in questions[:5])
        message_parts.append("")
        message_parts.append("Once you provide this information, we will continue processing.")

    return {
        "case_message": "\n".join(message_parts),
        "questions": questions[:5],
        "missing_fields": completeness_result["missing_fields"][:5],
        "completeness_score": completeness_result["completeness"],
    }
