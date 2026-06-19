from typing import Any

from sqlalchemy import select, and_

from app.models.memory import Memory
from app.services.database import async_session


async def get_memories_by_entity(entity_id: str, domain: str | None = None) -> list[dict[str, Any]]:
    async with async_session() as session:
        stmt = select(Memory).where(Memory.entity_id == entity_id)
        if domain:
            stmt = stmt.where(Memory.domain == domain)
        stmt = stmt.order_by(Memory.importance.desc(), Memory.created_at.desc()).limit(20)
        result = await session.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]


async def get_memories_by_department(department: str, limit: int = 10) -> list[dict[str, Any]]:
    async with async_session() as session:
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
        result = await session.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]


async def get_organizational_memories(limit: int = 10) -> list[dict[str, Any]]:
    async with async_session() as session:
        stmt = (
            select(Memory)
            .where(Memory.memory_type == "organizational")
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]


async def search_memories(query: str, memory_type: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    async with async_session() as session:
        stmt = select(Memory)
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)
        stmt = stmt.order_by(Memory.importance.desc()).limit(limit)
        result = await session.execute(stmt)
        return [m.to_dict() for m in result.scalars().all()]


async def store_memory(data: dict[str, Any]) -> dict[str, Any]:
    async with async_session() as session:
        mem = Memory(
            memory_type=data["memory_type"],
            domain=data["domain"],
            entity_id=data["entity_id"],
            content=data["content"],
            importance=data.get("importance", 50.0),
            department=data.get("department"),
            agent_id=data.get("agent_id"),
        )
        session.add(mem)
        await session.commit()
        return mem.to_dict()
