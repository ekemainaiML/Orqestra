import asyncio
import json
import uuid
from pathlib import Path

from sqlalchemy import select

from app.models import Customer, Memory
from app.services.database import get_async_session


def load_json(name: str) -> list[dict]:
    path = Path(__file__).parent / name
    return json.loads(path.read_text())


async def seed():
    async with get_async_session()() as session:
        existing = await session.execute(select(Customer).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        customers = load_json("customers.json")
        for c in customers:
            session.add(Customer(id=uuid.UUID(c["id"]), name=c["name"], email=c["email"], company=c.get("company"), notes=c.get("notes")))
        await session.flush()

        memories = load_json("memories.json")
        for m in memories:
            session.add(Memory(
                memory_type=m["memory_type"], domain=m["domain"], entity_id=m["entity_id"],
                content=m["content"], importance=m["importance"], department=m.get("department"),
                agent_id=m.get("agent_id"),
            ))

        await session.commit()
        print(f"Seeded {len(customers)} customers, {len(memories)} memories")


if __name__ == "__main__":
    asyncio.run(seed())
