import uuid

import pytest

from app.memory.memory_service import MemoryService
from app.memory.memory_promotion import calculate_importance, should_promote
from app.memory.queries import store_memory, get_organizational_memories, get_memories_by_entity, search_memories


class TestMemoryPromotion:

    def test_calculate_importance_from_decision(self):
        event = {"event_type": "decision_generated", "payload": {"confidence": 0.85}}
        importance = calculate_importance(event)
        assert 0.0 <= importance <= 1.0

    def test_calculate_importance_from_escalation_type(self):
        event = {"event_type": "escalation", "payload": {"reason": "Deadlock", "business_impact": 50}}
        importance = calculate_importance(event)
        assert importance == 55

    def test_calculate_importance_with_business_impact(self):
        event = {"event_type": "decision_generated", "payload": {"business_impact": 50, "actor": "sales"}}
        importance = calculate_importance(event)
        assert importance >= 40

    def test_calculate_importance_minor_event(self):
        event = {"event_type": "recommendation_submitted", "payload": {}}
        importance = calculate_importance(event)
        assert importance == 0

    def test_should_promote_decision_generated(self):
        assert should_promote({"event_type": "decision_generated"}) is True

    def test_should_promote_decision_approved(self):
        assert should_promote({"event_type": "decision_approved"}) is True

    def test_should_not_promote_low_importance_event(self):
        assert should_promote({"event_type": "memory_retrieved"}) is False


class TestMemoryQueries:

    async def test_store_and_retrieve_organizational_memory(self, db_session):
        memory = await store_memory({
            "memory_type": "organizational",
            "domain": "decision",
            "entity_id": str(uuid.uuid4()),
            "content": {"summary": "Test memory", "key_lesson": "Test lesson"},
            "importance": 0.8,
        }, session=db_session)
        assert memory["id"] is not None
        assert memory["importance"] == 0.8

        org_memories = await get_organizational_memories(limit=10, session=db_session)
        assert len(org_memories) >= 1
        assert any(m["id"] == memory["id"] for m in org_memories)

    async def test_store_and_retrieve_by_entity(self, db_session):
        entity_id = str(uuid.uuid4())
        await store_memory({
            "memory_type": "operational",
            "domain": "customer",
            "entity_id": entity_id,
            "content": {"summary": "Customer specific memory"},
            "importance": 0.6,
        }, session=db_session)
        results = await get_memories_by_entity(entity_id, domain="customer", session=db_session)
        assert len(results) >= 1

    async def test_search_memories(self, db_session):
        await store_memory({
            "memory_type": "organizational",
            "domain": "decision",
            "entity_id": str(uuid.uuid4()),
            "content": {"summary": "Volume discount policy for large orders"},
            "importance": 0.7,
        }, session=db_session)
        results = await search_memories("discount", limit=10, session=db_session)
        assert len(results) >= 1
        assert any("discount" in m["content"].get("summary", "").lower() for m in results)


class TestMemoryService:

    async def test_retrieve_for_case_returns_memories(self, db_session, seed_customers):
        service = MemoryService()
        memories = await service.retrieve_for_case(
            customer_id=str(seed_customers[0].id), session=db_session,
        )
        assert isinstance(memories, list)

    async def test_evaluate_and_store_promotable_event(self, db_session):
        service = MemoryService()
        event = {
            "case_id": str(uuid.uuid4()),
            "event_type": "decision_generated",
            "actor": "operations_manager",
            "payload": {"summary": "Approved 500 units", "confidence": 0.85, "key_lesson": "Government orders need extra margin review"},
        }
        result = await service.evaluate_and_store(event, session=db_session)
        assert result is not None
        assert result["importance"] > 0.5

    async def test_evaluate_and_store_non_promotable_event(self, db_session):
        service = MemoryService()
        event = {
            "case_id": str(uuid.uuid4()),
            "event_type": "memory_retrieved",
            "actor": "system",
            "payload": {},
        }
        result = await service.evaluate_and_store(event, session=db_session)
        assert result is None
