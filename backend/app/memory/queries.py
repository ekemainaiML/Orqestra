from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory


async def get_memories_by_entity(entity_id: str, domain: str | None = None, session: AsyncSession | None = None) -> list[dict[str, Any]]:
    async def _do(s: AsyncSession) -> list[dict[str, Any]]:
        stmt = select(Memory).where(Memory.entity_id == entity_id)
        if domain:
            stmt = stmt.where(Memory.domain == domain)
        stmt = stmt.order_by(Memory.importance.desc(), Memory.created_at.desc()).limit(20)
        result = await s.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def get_memories_by_department(department: str, limit: int = 10, session: AsyncSession | None = None) -> list[dict[str, Any]]:
    async def _do(s: AsyncSession) -> list[dict[str, Any]]:
        stmt = (
            select(Memory)
            .where(
                and_(
                    Memory.department == department,
                    Memory.memory_type == "department",
                )
            )
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        result = await s.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def get_organizational_memories(limit: int = 10, session: AsyncSession | None = None) -> list[dict[str, Any]]:
    async def _do(s: AsyncSession) -> list[dict[str, Any]]:
        stmt = (
            select(Memory)
            .where(Memory.memory_type == "organizational")
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        result = await s.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def search_memories(query: str, memory_type: str | None = None, limit: int = 10, session: AsyncSession | None = None) -> list[dict[str, Any]]:
    async def _do(s: AsyncSession) -> list[dict[str, Any]]:
        stmt = select(Memory)
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)
        stmt = stmt.order_by(Memory.importance.desc()).limit(limit)
        result = await s.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)


async def store_memory(data: dict[str, Any], session: AsyncSession | None = None) -> dict[str, Any]:
    async def _do(s: AsyncSession) -> dict[str, Any]:
        mem = Memory(
            memory_type=data["memory_type"],
            domain=data["domain"],
            entity_id=data["entity_id"],
            content=data["content"],
            importance=data.get("importance", 50.0),
            department=data.get("department"),
            agent_id=data.get("agent_id"),
        )
        s.add(mem)
        await s.commit()
        return mem.to_dict()

    if session is not None:
        return await _do(session)
    from app.services.database import get_async_session
    s = get_async_session()()
    async with s:
        return await _do(s)
