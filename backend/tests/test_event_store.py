import uuid

import pytest

from app.events.event_store import append_event, get_events, get_event_count


class TestEventStore:

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_append_and_retrieve_event(self, seed_case):
        case_id = str(seed_case.id)
        event = await append_event(case_id, "case_created", "system", {"test": True})
        assert event["case_id"] == case_id
        assert event["event_type"] == "case_created"
        assert event["actor"] == "system"
        assert event["payload"] == {"test": True}

        events = await get_events(case_id)
        assert len(events) >= 1
        assert events[-1]["event_type"] == "case_created"

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_get_events_by_type(self, seed_case):
        case_id = str(seed_case.id)
        await append_event(case_id, "memory_retrieved", "system", {})
        await append_event(case_id, "recommendation_submitted", "sales", {})
        await append_event(case_id, "recommendation_submitted", "finance", {})

        rec_events = await get_events(case_id, event_type="recommendation_submitted")
        assert len(rec_events) == 2

        mem_events = await get_events(case_id, event_type="memory_retrieved")
        assert len(mem_events) == 1

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_get_events_by_iteration(self, seed_case):
        case_id = str(seed_case.id)
        await append_event(case_id, "iteration_started", "system", {}, iteration=1)
        await append_event(case_id, "recommendation_submitted", "sales", {}, iteration=1)
        await append_event(case_id, "iteration_started", "system", {}, iteration=2)

        it1 = await get_events(case_id, iteration=1)
        assert len(it1) == 2

        it2 = await get_events(case_id, iteration=2)
        assert len(it2) == 1

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_get_event_count(self, seed_case):
        case_id = str(seed_case.id)
        count_before = await get_event_count(case_id)
        await append_event(case_id, "test_event", "system", {})
        count_after = await get_event_count(case_id)
        assert count_after == count_before + 1

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_get_events_empty_case(self):
        events = await get_events(str(uuid.uuid4()))
        assert events == []

    @pytest.mark.skip(reason="Needs DB session injection refactor — event_store uses global async_session")
    async def test_get_event_count_empty_case(self):
        count = await get_event_count(str(uuid.uuid4()))
        assert count == 0
