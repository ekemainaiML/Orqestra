import uuid

import pytest

from app.events.event_store import append_event, get_events, get_event_count


class TestEventStore:

    async def test_append_and_retrieve_event(self, db_session, seed_case):
        case_id = str(seed_case.id)
        event = await append_event(case_id, "case_created", "system", {"test": True}, session=db_session)
        assert event["case_id"] == case_id
        assert event["event_type"] == "case_created"
        assert event["actor"] == "system"
        assert event["payload"] == {"test": True}

        events = await get_events(case_id, session=db_session)
        assert len(events) >= 1
        assert events[-1]["event_type"] == "case_created"

    async def test_get_events_by_type(self, db_session, seed_case):
        case_id = str(seed_case.id)
        await append_event(case_id, "memory_retrieved", "system", {}, session=db_session)
        await append_event(case_id, "recommendation_submitted", "sales", {}, session=db_session)
        await append_event(case_id, "recommendation_submitted", "finance", {}, session=db_session)

        rec_events = await get_events(case_id, event_type="recommendation_submitted", session=db_session)
        assert len(rec_events) == 2

        mem_events = await get_events(case_id, event_type="memory_retrieved", session=db_session)
        assert len(mem_events) == 1

    async def test_get_events_by_iteration(self, db_session, seed_case):
        case_id = str(seed_case.id)
        await append_event(case_id, "iteration_started", "system", {}, iteration=1, session=db_session)
        await append_event(case_id, "recommendation_submitted", "sales", {}, iteration=1, session=db_session)
        await append_event(case_id, "iteration_started", "system", {}, iteration=2, session=db_session)

        it1 = await get_events(case_id, iteration=1, session=db_session)
        assert len(it1) == 2

        it2 = await get_events(case_id, iteration=2, session=db_session)
        assert len(it2) == 1

    async def test_get_event_count(self, db_session, seed_case):
        case_id = str(seed_case.id)
        count_before = await get_event_count(case_id, session=db_session)
        await append_event(case_id, "test_event", "system", {}, session=db_session)
        count_after = await get_event_count(case_id, session=db_session)
        assert count_after == count_before + 1

    async def test_get_events_empty_case(self, db_session):
        events = await get_events(str(uuid.uuid4()), session=db_session)
        assert events == []

    async def test_get_event_count_empty_case(self, db_session):
        count = await get_event_count(str(uuid.uuid4()), session=db_session)
        assert count == 0
