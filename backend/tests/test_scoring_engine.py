from app.deliberation.scoring_engine import (
    AGENT_EXPERTISE,
    SCORE_DIMENSIONS,
    _score_from_recommendation,
    _estimate_risk_count,
    calculate_scores,
)


class TestScoreFromRecommendation:

    def test_customer_satisfaction_keywords(self):
        rec = {
            "agent_id": "sales",
            "recommendation": "Proceed with order. Customer satisfaction is high. Quality service ensured.",
            "reasoning": "Strong client relationship and feedback.",
            "confidence": 0.85,
            "risks": [],
            "alternatives": [],
        }
        score = _score_from_recommendation(rec, "customer_satisfaction")
        assert 0.3 <= score <= 1.0

    def test_profitability_keywords(self):
        rec = {
            "agent_id": "finance",
            "recommendation": "Budget approved. Margin at 28%. Revenue target achieved.",
            "reasoning": "Cost structure and pricing aligned.",
            "confidence": 0.78,
            "risks": [],
            "alternatives": [],
        }
        score = _score_from_recommendation(rec, "profitability")
        assert 0.3 <= score <= 1.0

    def test_empty_recommendation_returns_baseline(self):
        rec = {"agent_id": "sales", "recommendation": "", "reasoning": "", "risks": [], "alternatives": [], "confidence": 0.5}
        score = _score_from_recommendation(rec, "customer_satisfaction")
        assert score == 0.5

    def test_high_confidence_boosts_score(self):
        low_conf = {
            "agent_id": "sales", "recommendation": "customer client satisfaction",
            "reasoning": "", "confidence": 0.1, "risks": [], "alternatives": [],
        }
        high_conf = {
            "agent_id": "sales", "recommendation": "customer client satisfaction",
            "reasoning": "", "confidence": 0.95, "risks": [], "alternatives": [],
        }
        low_score = _score_from_recommendation(low_conf, "customer_satisfaction")
        high_score = _score_from_recommendation(high_conf, "customer_satisfaction")
        assert high_score > low_score

    def test_unknown_dimension_returns_baseline(self):
        rec = {"agent_id": "sales", "recommendation": "Some text", "reasoning": "", "confidence": 0.5, "risks": [], "alternatives": []}
        score = _score_from_recommendation(rec, "nonexistent_dimension")
        assert score == 0.5


class TestEstimateRiskCount:

    def test_deduplicates_identical_risks(self):
        recs = [
            {"agent_id": "a", "risks": ["Shortfall of 100 units", "Delivery delay"]},
            {"agent_id": "b", "risks": ["Shortfall of 100 units", "Payment risk"]},
        ]
        risks = _estimate_risk_count(recs)
        assert len(risks) == 3
        assert "Shortfall of 100 units" in risks
        assert "Delivery delay" in risks
        assert "Payment risk" in risks

    def test_case_insensitive_dedup(self):
        recs = [
            {"agent_id": "a", "risks": ["Shortfall of 100 units"]},
            {"agent_id": "b", "risks": ["SHORTFALL OF 100 UNITS"]},
        ]
        risks = _estimate_risk_count(recs)
        assert len(risks) == 1

    def test_no_risks_returns_empty(self):
        recs = [{"agent_id": "a", "risks": []}, {"agent_id": "b", "risks": []}]
        assert _estimate_risk_count(recs) == []


class TestCalculateScores:

    def test_returns_expected_structure(self, sample_recommendations):
        result = calculate_scores(sample_recommendations)
        assert "overall_consensus" in result
        assert "dimension_scores" in result
        assert "agent_scores" in result
        assert "risks" in result
        assert "score_breakdown" in result

    def test_overall_consensus_is_reasonable(self, sample_recommendations):
        result = calculate_scores(sample_recommendations)
        assert 0.0 <= result["overall_consensus"] <= 1.0

    def test_all_dimensions_scored(self, sample_recommendations):
        result = calculate_scores(sample_recommendations)
        for dim in SCORE_DIMENSIONS:
            assert dim in result["dimension_scores"]
            assert 0.0 <= result["dimension_scores"][dim] <= 1.0

    def test_agents_only_score_their_expertise_domains(self, sample_recommendations):
        result = calculate_scores(sample_recommendations)
        for agent_id, dims in result["agent_scores"].items():
            expected_dims = AGENT_EXPERTISE.get(agent_id, [])
            for dim in dims:
                assert dim in expected_dims, f"Agent {agent_id} scored dimension {dim} outside expertise"

    def test_risks_identified(self, sample_recommendations):
        result = calculate_scores(sample_recommendations)
        assert len(result["risks"]) > 0

    def test_empty_recommendations(self):
        result = calculate_scores([])
        assert result["overall_consensus"] == 0.0
        assert result["risks"] == []
