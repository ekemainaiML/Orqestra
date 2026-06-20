from app.api.benchmark import _parse_case_text, _build_single_recommendation, _build_org_recommendations


class TestParseCaseText:

    def test_standard_government_order(self):
        text = "Government order — 500 solar-powered street lights for municipal lighting project. 100W preferred."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 500
        assert parsed["product"] == "solar_street_light_100w"
        assert parsed["is_government"] is True
        assert parsed["is_urgent"] is False

    def test_urgent_private_order(self):
        text = "Urgent — 30 units needed ASAP for office park. 60W lights. Private company."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 30
        assert parsed["product"] == "solar_street_light_60w"
        assert parsed["is_government"] is False
        assert parsed["is_urgent"] is True

    def test_private_order_with_street_lights(self):
        text = "Need 300 solar street lights, 100W. Delivery in 21 days. Private sector."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 300
        assert parsed["product"] == "solar_street_light_100w"
        assert parsed["is_government"] is False
        assert parsed["deadline_days"] == 21

    def test_default_quantity_when_no_match(self):
        text = "We need lights for our project."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 100

    def test_deadline_in_weeks(self):
        text = "Need 100 pieces. Delivery in 3 weeks."
        parsed = _parse_case_text(text)
        assert parsed["deadline_days"] == 21

    def test_municipal_detected_as_government(self):
        text = "Order for municipal council project — 50 lights."
        parsed = _parse_case_text(text)
        assert parsed["is_government"] is True

    def test_rush_detected_as_urgent(self):
        text = "Rush order — 200 units for immediate deployment."
        parsed = _parse_case_text(text)
        assert parsed["is_urgent"] is True

    def test_small_order_no_discount(self):
        text = "Just 10 units for a small office."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 10

    def test_large_order_qualifies_for_volume_discount(self):
        text = "Need 400 pieces for nationwide rollout."
        parsed = _parse_case_text(text)
        assert parsed["quantity"] == 400


def _make_tools(quantity=100, unit_price=195.0, margin_pct=38.5, shortfall=0, available=100):
    return {
        "pricing": {
            "unit_price": unit_price,
            "subtotal": unit_price * quantity,
            "estimated_margin_pct": margin_pct,
            "volume_discount_applied": quantity >= 250,
            "preferred_discount_applied": False,
        },
        "inventory": {
            "product": "solar_street_light_100w",
            "requested": quantity,
            "available": available,
            "shortfall": shortfall,
            "needs_procurement": shortfall > 0,
        },
        "suppliers": [
            {"name": "SolarTech Manufacturing", "lead_time_days": 14, "region": "domestic", "reliability": 0.95},
            {"name": "AfriEnergy Components", "lead_time_days": 10, "region": "regional", "reliability": 0.88},
        ],
        "policies": {
            "minimum_margin": {"compliant": True, "details": ""},
            "new_client_deposit": {"compliant": True, "details": ""},
        },
    }


class TestBuildSingleRecommendation:

    def test_includes_procurement_when_shortfall(self):
        parsed = {"quantity": 500, "product": "solar_street_light_100w", "is_government": True, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=500, unit_price=166.72, margin_pct=28.0, shortfall=350, available=150)
        rec = _build_single_recommendation(parsed, tools)
        assert "Procurement needed for 350 units" in rec["recommendation"]
        assert rec["confidence"] < 0.6

    def test_no_procurement_when_sufficient_stock(self):
        parsed = {"quantity": 30, "product": "solar_street_light_60w", "is_government": False, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=30, available=200, shortfall=0)
        rec = _build_single_recommendation(parsed, tools)
        assert "Procurement needed" not in rec["recommendation"]
        assert rec["confidence"] > 0.5

    def test_urgent_with_shortfall_adds_risk(self):
        parsed = {"quantity": 100, "product": "solar_street_light_100w", "is_government": False, "is_urgent": True, "deadline_days": 14}
        tools = _make_tools(quantity=100, shortfall=50, available=50)
        rec = _build_single_recommendation(parsed, tools)
        risk_texts = [r.lower() for r in rec["risks"]]
        assert any("urgent" in r or "procurement" in r for r in risk_texts)

    def test_tight_deadline_adds_risk(self):
        parsed = {"quantity": 50, "product": "solar_street_light_100w", "is_government": False, "is_urgent": False, "deadline_days": 5}
        tools = _make_tools(quantity=50, shortfall=0, available=100)
        rec = _build_single_recommendation(parsed, tools)
        risk_texts = [r.lower() for r in rec["risks"]]
        assert any("air freight" in r or "delivery window" in r for r in risk_texts)

    def test_government_client_adds_factor(self):
        parsed = {"quantity": 500, "product": "solar_street_light_100w", "is_government": True, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=500, shortfall=0, available=500)
        rec = _build_single_recommendation(parsed, tools)
        assert any("government" in f.lower() for f in rec.get("factors", []))

    def test_govt_pricing_lower_margin(self):
        parsed = {"quantity": 500, "product": "solar_street_light_100w", "is_government": True, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=500, unit_price=166.72, margin_pct=28.0, shortfall=0, available=500)
        rec = _build_single_recommendation(parsed, tools)
        assert "$166.72" in rec["recommendation"]
        assert "28.0%" in rec["recommendation"]


class TestBuildOrgRecommendations:

    def test_returns_six_recommendations(self):
        parsed = {"quantity": 100, "product": "solar_street_light_100w", "is_government": False, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=100, shortfall=0, available=100)
        recs = _build_org_recommendations(parsed, tools)
        assert len(recs) == 6

    def test_last_recommendation_is_operations_manager(self):
        parsed = {"quantity": 100, "product": "solar_street_light_100w", "is_government": False, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=100, shortfall=0, available=100)
        recs = _build_org_recommendations(parsed, tools)
        assert recs[-1]["agent_id"] == "operations_manager"

    def test_inventory_confidence_low_when_shortfall(self):
        parsed = {"quantity": 500, "product": "solar_street_light_100w", "is_government": True, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=500, shortfall=350, available=150)
        recs = _build_org_recommendations(parsed, tools)
        inv_rec = next(r for r in recs if r["agent_id"] == "inventory")
        assert inv_rec["confidence"] == 0.3

    def test_inventory_confidence_high_when_no_shortfall(self):
        parsed = {"quantity": 30, "product": "solar_street_light_60w", "is_government": False, "is_urgent": False, "deadline_days": 14}
        tools = _make_tools(quantity=30, shortfall=0, available=200)
        recs = _build_org_recommendations(parsed, tools)
        inv_rec = next(r for r in recs if r["agent_id"] == "inventory")
        assert inv_rec["confidence"] == 0.7

    def test_logistics_urgency_flag(self):
        parsed = {"quantity": 100, "product": "solar_street_light_100w", "is_government": False, "is_urgent": True, "deadline_days": 14}
        tools = _make_tools(shortfall=0, available=100)
        recs = _build_org_recommendations(parsed, tools)
        log_rec = next(r for r in recs if r["agent_id"] == "logistics")
        assert "URGENT" in log_rec["recommendation"]
