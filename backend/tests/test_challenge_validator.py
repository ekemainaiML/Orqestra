import pytest

from app.deliberation.challenge_validator import (
    validate_challenge,
    route_challenge_to_agents,
    process_challenges,
    generate_challenge_id,
)
from app.agents.base import Challenge


class TestValidateChallenge:

    async def test_valid_challenge_passes(self):
        result = await validate_challenge({
            "challenge_type": "factual_error",
            "target_agent": "finance",
            "statement": "The margin calculation is wrong",
            "evidence": [{"source": "inventory", "note": "Stock levels differ"}],
            "confidence": 0.8,
        })
        assert result["valid"] is True

    async def test_missing_fields_rejected(self):
        result = await validate_challenge({
            "challenge_type": "factual_error",
        })
        assert result["valid"] is False
        assert "Missing" in result["reason"]

    async def test_invalid_challenge_type_rejected(self):
        result = await validate_challenge({
            "challenge_type": "invalid_type",
            "target_agent": "finance",
            "statement": "Test",
            "evidence": [{"note": "test"}],
            "confidence": 0.5,
        })
        assert result["valid"] is False
        assert "Invalid challenge type" in result["reason"]

    async def test_empty_evidence_rejected(self):
        result = await validate_challenge({
            "challenge_type": "assumption_flaw",
            "target_agent": "finance",
            "statement": "Test",
            "evidence": [],
            "confidence": 0.5,
        })
        assert result["valid"] is False

    async def test_confidence_out_of_range_rejected(self):
        result = await validate_challenge({
            "challenge_type": "risk_underestimation",
            "target_agent": "logistics",
            "statement": "Test",
            "evidence": [{"note": "test"}],
            "confidence": 1.5,
        })
        assert result["valid"] is False
        assert "Confidence" in result["reason"]

    async def test_all_valid_types_accepted(self):
        for ct in ["factual_error", "assumption_flaw", "missing_evidence",
                    "risk_underestimation", "policy_violation", "cost_miscalculation"]:
            result = await validate_challenge({
                "challenge_type": ct,
                "target_agent": "sales",
                "statement": "Test statement",
                "evidence": [{"source": "audit", "note": "Reviewed"}],
                "confidence": 0.6,
            })
            assert result["valid"] is True, f"Type {ct} should be valid"


class TestRouteChallenge:

    async def test_excludes_source_agent(self):
        c = Challenge(challenge_id="ch-1", source_agent="sales", target_agent="finance",
                       challenge_type="assumption_flaw", statement="test",
                       evidence=[], confidence=0.5)
        targets = await route_challenge_to_agents(c, ["sales", "finance", "inventory"])
        assert "sales" not in targets
        assert len(targets) == 2

    async def test_single_agent_returns_empty(self):
        c = Challenge(challenge_id="ch-1", source_agent="sales", target_agent="finance",
                       challenge_type="assumption_flaw", statement="test",
                       evidence=[], confidence=0.5)
        targets = await route_challenge_to_agents(c, ["sales"])
        assert targets == []


class TestGenerateChallengeId:

    async def test_returns_uuid_string(self):
        cid = await generate_challenge_id()
        assert isinstance(cid, str)
        assert len(cid) == 36


class TestProcessChallenges:

    async def test_empty_recommendations_returns_no_challenges(self):
        result = await process_challenges([], ["sales"])
        assert result["challenges"] == []
        assert result["total_issued"] == 0

    async def test_single_recommendation_no_cross_agent(self):
        recs = [{"agent_id": "sales", "recommendation": "Proceed"}]
        result = await process_challenges(recs, ["sales"])
        assert result["challenges"] == []
        assert result["total_issued"] == 0

    async def test_two_agents_produces_challenges(self):
        recs = [
            {"agent_id": "sales", "recommendation": "Proceed with 100 units"},
            {"agent_id": "finance", "recommendation": "Need more margin"},
        ]
        result = await process_challenges(recs, ["sales", "finance"])
        assert result["total_issued"] > 0
        for ch in result["challenges"]:
            assert "challenge_id" in ch
            assert ch["source_agent"] != ch["target_agent"]

    async def test_all_agents_challenge_each_other(self):
        recs = [
            {"agent_id": "sales", "recommendation": "Sell"},
            {"agent_id": "inventory", "recommendation": "Check stock"},
            {"agent_id": "finance", "recommendation": "Review budget"},
        ]
        result = await process_challenges(recs, ["sales", "inventory", "finance"])
        assert result["total_issued"] > 0
        seen = set()
        for ch in result["challenges"]:
            pair = (ch["source_agent"], ch["target_agent"])
            assert pair not in seen, f"Duplicate challenge: {pair}"
            seen.add(pair)
