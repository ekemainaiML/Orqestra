from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.memory_promotion import calculate_importance, should_promote
from app.memory.queries import (
    get_memories_by_department,
    get_memories_by_entity,
    get_organizational_memories,
    store_memory,
)


class MemoryService:

    async def retrieve_for_agent(
        self, agent_id: str, department: str | None, customer_id: str | None, supplier_ids: list[str] | None,
        session: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        memories = []
        org = await get_organizational_memories(limit=5, session=session)
        memories.extend(org)

        if department:
            dept = await get_memories_by_department(department, limit=5, session=session)
            memories.extend(dept)

        if customer_id:
            customer = await get_memories_by_entity(customer_id, domain="customer", session=session)
            memories.extend(customer)

        if supplier_ids:
            for sid in supplier_ids:
                supplier = await get_memories_by_entity(sid, domain="supplier", session=session)
                memories.extend(supplier)

        memories.sort(key=lambda m: m.get("importance", 0), reverse=True)
        return memories[:10]

    async def retrieve_for_case(
        self, customer_id: str | None = None, supplier_ids: list[str] | None = None,
        session: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        memories = await get_organizational_memories(limit=5, session=session)
        if customer_id:
            customer = await get_memories_by_entity(customer_id, session=session)
            memories.extend(customer)
        if supplier_ids:
            for sid in supplier_ids:
                supplier = await get_memories_by_entity(sid, session=session)
                memories.extend(supplier)
        return memories[:15]

    async def evaluate_and_store(
        self, event: dict[str, Any],
        session: AsyncSession | None = None,
    ) -> dict[str, Any] | None:
        importance = calculate_importance(event)
        if not should_promote(event):
            return None

        payload = event.get("payload", {})
        memory_data = {
            "memory_type": "organizational",
            "domain": "decision",
            "entity_id": event.get("case_id", ""),
            "content": {
                "summary": payload.get("summary", ""),
                "event_type": event.get("event_type"),
                "actor": event.get("actor"),
                "key_lesson": payload.get("key_lesson", ""),
            },
            "importance": importance,
        }
        return await store_memory(memory_data, session=session)
