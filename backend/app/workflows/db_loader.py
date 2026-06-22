import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_config import WorkflowConfigModel
from app.workflows.loader import list_workflow_types as list_filesystem_types
from app.workflows.schema import WorkflowConfig

BUILTIN_PREFIX = "builtin:"


def _is_builtin_type(wt: str) -> bool:
    return wt.startswith(BUILTIN_PREFIX)


def _strip_builtin_prefix(wt: str) -> str:
    return wt[len(BUILTIN_PREFIX):] if _is_builtin_type(wt) else wt


async def list_all_workflow_types(session: AsyncSession) -> list[str]:
    filesystem_types = [f"{BUILTIN_PREFIX}{t}" for t in list_filesystem_types()]
    result = await session.execute(select(WorkflowConfigModel.id))
    db_types = [row[0] for row in result]
    return sorted(set(filesystem_types + db_types))


async def load_workflow_config(session: AsyncSession, wt: str) -> WorkflowConfig | None:
    if _is_builtin_type(wt):
        raw = _strip_builtin_prefix(wt)
        from app.workflows.loader import load_workflow_config as load_file_config
        return load_file_config(raw)

    result = await session.execute(
        select(WorkflowConfigModel).where(WorkflowConfigModel.id == wt)
    )
    model = result.scalar_one_or_none()
    if model is None:
        return None

    data = yaml.safe_load(model.yaml_content)
    return WorkflowConfig(**data)


async def list_all_configs(session: AsyncSession) -> list[dict]:
    configs: dict[str, dict] = {}

    for wt in list_filesystem_types():
        from app.workflows.loader import load_workflow_config as load_file_config
        cfg = load_file_config(wt)
        configs[cfg.id] = {**cfg.model_dump_flat(), "is_builtin": True}

    result = await session.execute(select(WorkflowConfigModel))
    for row in result.scalars():
        try:
            data = yaml.safe_load(row.yaml_content)
            cfg = WorkflowConfig(**data)
            configs[cfg.id] = {**cfg.model_dump_flat(), "is_builtin": False}
        except Exception:
            configs[row.id] = {
                "id": row.id,
                "name": row.name,
                "is_builtin": False,
                "departments": [],
                "decision_dimensions": [],
                "consensus_threshold": 0.0,
                "policies": [],
                "required_role": "",
            }

    return list(configs.values())


async def save_workflow_config(
    session: AsyncSession,
    config_id: str,
    name: str,
    yaml_content: str,
) -> WorkflowConfigModel:
    existing = await session.execute(
        select(WorkflowConfigModel).where(WorkflowConfigModel.id == config_id)
    )
    model = existing.scalar_one_or_none()
    if model:
        model.name = name
        model.yaml_content = yaml_content
    else:
        model = WorkflowConfigModel(
            id=config_id,
            name=name,
            yaml_content=yaml_content,
            is_builtin=False,
        )
        session.add(model)
    await session.commit()
    return model


async def delete_workflow_config(session: AsyncSession, config_id: str) -> bool:
    result = await session.execute(
        select(WorkflowConfigModel).where(
            WorkflowConfigModel.id == config_id,
            not WorkflowConfigModel.is_builtin,
        )
    )
    model = result.scalar_one_or_none()
    if model is None:
        return False
    await session.delete(model)
    await session.commit()
    return True
