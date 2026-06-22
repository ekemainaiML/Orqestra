
import yaml
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import get_agent_class, get_all_agent_ids
from app.services.database import get_session
from app.workflows.db_loader import delete_workflow_config, list_all_configs, save_workflow_config
from app.workflows.schema import WorkflowConfig

router = APIRouter(prefix="/admin", tags=["admin"])


class ValidationRequest(BaseModel):
    yaml_content: str


class ValidationResult(BaseModel):
    valid: bool
    workflow_id: str | None = None
    workflow_name: str | None = None
    errors: list[str] = []
    warnings: list[str] = []
    summary: dict | None = None


@router.post("/workflows/validate", response_model=ValidationResult)
async def validate_workflow_config(req: ValidationRequest):
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = yaml.safe_load(req.yaml_content)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return ValidationResult(valid=False, errors=errors)

    if not isinstance(data, dict):
        errors.append("YAML root must be a mapping (workflow config object)")
        return ValidationResult(valid=False, errors=errors)

    try:
        config = WorkflowConfig(**data)
    except Exception as e:
        errors.append(f"Schema validation failed: {e}")
        return ValidationResult(valid=False, errors=errors)

    known_agents = set(get_all_agent_ids())

    for dept in config.departments:
        if dept.id not in known_agents:
            errors.append(
                f"Department '{dept.id}' (role: {dept.role}) has no registered agent class. "
                f"Known agents: {', '.join(sorted(known_agents))}"
            )
        else:
            try:
                get_agent_class(dept.id)
            except ValueError as e:
                errors.append(str(e))

    executive_id = config.approval.required_role
    if executive_id not in known_agents:
        errors.append(
            f"Executive agent '{executive_id}' (required_role) not found in agent registry. "
            f"Known agents: {', '.join(sorted(known_agents))}"
        )

    executive_ids = [d.id for d in config.departments]
    if executive_id not in executive_ids:
        warnings.append(
            f"Executive agent '{executive_id}' is not listed in the departments. "
            f"A department with id='{executive_id}' should exist."
        )

    if config.governance.consensus_threshold < 0.5:
        warnings.append(
            f"Consensus threshold ({config.governance.consensus_threshold}) is very low. "
            "Consider raising it above 0.5."
        )

    if len(config.departments) < 2:
        warnings.append(
            f"Only {len(config.departments)} department(s) defined. "
            "Multi-agent deliberation typically requires at least 2 operational departments."
        )

    operational = config.get_operational_departments()
    if not operational:
        warnings.append(
            "No operational departments found (all departments match required_role). "
            "At least one operational department is expected."
        )

    summary = {
        "workflow_id": config.id,
        "workflow_name": config.name,
        "departments": len(config.departments),
        "operational_departments": len(operational),
        "decision_dimensions": len(config.decision_dimensions),
        "policies": len(config.policies),
        "hard_constraints": sum(1 for p in config.policies if p.hard_constraint),
        "consensus_threshold": config.governance.consensus_threshold,
        "deadlock_resolution": config.governance.deadlock_resolution,
        "required_role": config.approval.required_role,
        "agents_resolved": sum(1 for d in config.departments if d.id in known_agents),
    }

    return ValidationResult(
        valid=len(errors) == 0,
        workflow_id=config.id,
        workflow_name=config.name,
        errors=errors,
        warnings=warnings,
        summary=summary,
    )


class SaveWorkflowRequest(BaseModel):
    yaml_content: str


class SaveWorkflowResponse(BaseModel):
    id: str
    name: str
    message: str


@router.post("/workflows", response_model=SaveWorkflowResponse)
async def save_workflow(req: SaveWorkflowRequest, session: AsyncSession = Depends(get_session)):
    try:
        data = yaml.safe_load(req.yaml_content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    try:
        config = WorkflowConfig(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Schema validation failed: {e}")

    model = await save_workflow_config(session, config.id, config.name, req.yaml_content)

    return SaveWorkflowResponse(
        id=model.id,
        name=model.name,
        message=f"Workflow '{model.name}' saved successfully",
    )


@router.get("/workflows")
async def list_workflows(session: AsyncSession = Depends(get_session)):
    configs = await list_all_configs(session)
    return {"workflows": configs}


@router.get("/workflows/{workflow_id}/export")
async def export_workflow(workflow_id: str, session: AsyncSession = Depends(get_session)):
    from app.workflows.db_loader import _is_builtin_type, _strip_builtin_prefix
    from app.workflows.loader import WORKFLOWS_DIR, load_workflow_config as load_file_config
    import os

    if _is_builtin_type(workflow_id):
        raw = _strip_builtin_prefix(workflow_id)
        load_file_config(raw)
        yaml_path = os.path.join(WORKFLOWS_DIR, f"{raw}.yaml")
        with open(yaml_path) as f:
            content = f.read()
    else:
        from app.models.workflow_config import WorkflowConfigModel
        from sqlalchemy import select
        result = await session.execute(
            select(WorkflowConfigModel).where(WorkflowConfigModel.id == workflow_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        content = model.yaml_content

    from starlette.responses import PlainTextResponse
    return PlainTextResponse(
        content,
        media_type="text/yaml",
        headers={"Content-Disposition": f'attachment; filename="{workflow_id}.yaml"'},
    )


@router.post("/workflows/import", response_model=SaveWorkflowResponse)
async def import_workflow(file: UploadFile, session: AsyncSession = Depends(get_session)):
    if not file.filename or not file.filename.endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="File must be a .yaml or .yml file")

    content = (await file.read()).decode("utf-8")

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="YAML root must be a mapping")

    try:
        config = WorkflowConfig(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Schema validation failed: {e}")

    model = await save_workflow_config(session, config.id, config.name, content)

    return SaveWorkflowResponse(
        id=model.id,
        name=model.name,
        message=f"Workflow '{model.name}' imported successfully",
    )


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, session: AsyncSession = Depends(get_session)):
    from app.workflows.db_loader import _is_builtin_type, _strip_builtin_prefix
    from app.workflows.loader import load_workflow_config as load_file_config

    if _is_builtin_type(workflow_id):
        raw = _strip_builtin_prefix(workflow_id)
        try:
            cfg = load_file_config(raw)
        except ValueError:
            raise HTTPException(status_code=404, detail="Workflow not found")
        filepath = f"{raw}.yaml"
        import os

        from app.workflows.loader import WORKFLOWS_DIR
        yaml_path = os.path.join(WORKFLOWS_DIR, filepath)
        with open(yaml_path) as f:
            yaml_content = f.read()
        return {
            "id": raw,
            "name": cfg.name,
            "is_builtin": True,
            "yaml_content": yaml_content,
            "config": cfg.model_dump_flat(),
        }

    from sqlalchemy import select

    from app.models.workflow_config import WorkflowConfigModel
    result = await session.execute(
        select(WorkflowConfigModel).where(WorkflowConfigModel.id == workflow_id)
    )
    model = result.scalar_one_or_none()
    if model is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    import yaml
    data = yaml.safe_load(model.yaml_content)
    cfg = WorkflowConfig(**data)
    return {
        "id": model.id,
        "name": model.name,
        "is_builtin": False,
        "yaml_content": model.yaml_content,
        "config": cfg.model_dump_flat(),
    }


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await delete_workflow_config(session, workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found or is built-in")
    return {"message": f"Workflow '{workflow_id}' deleted"}
