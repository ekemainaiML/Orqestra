"""
Seed workflow configs from YAML files into the database.
Run:  python -m scripts.seed_workflows
"""

import asyncio
import os

import yaml
from sqlalchemy import select

WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "workflows")


async def seed():
    from app.models import Base, WorkflowConfigModel
    from app.services.database import get_async_session, get_engine

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_async_session()() as session:
        yaml_files = sorted(
            f for f in os.listdir(WORKFLOWS_DIR)
            if f.endswith(".yaml") and f != "__init__.yaml"
        )

        for fname in yaml_files:
            config_id = fname.removesuffix(".yaml")
            filepath = os.path.join(WORKFLOWS_DIR, fname)

            with open(filepath) as f:
                yaml_content = f.read()

            data = yaml.safe_load(yaml_content)
            name = data.get("name", config_id.replace("_", " ").title())

            existing = await session.scalar(
                select(WorkflowConfigModel).where(WorkflowConfigModel.id == config_id)
            )
            if existing:
                print(f"  ~ {config_id} already exists, skipping")
                continue

            model = WorkflowConfigModel(
                id=config_id,
                name=name,
                yaml_content=yaml_content,
                is_builtin=True,
            )
            session.add(model)
            print(f"  ✓ Seeded workflow '{config_id}' ({name})")

        await session.commit()
        print(f"\n  Done. {len(yaml_files)} workflow(s) seeded.")

    await get_engine().dispose()


if __name__ == "__main__":
    asyncio.run(seed())
