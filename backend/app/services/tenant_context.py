import contextvars
import uuid

from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

_current_tenant_id: contextvars.ContextVar[uuid.UUID | None] = (
    contextvars.ContextVar("current_tenant_id", default=None)
)


def get_current_tenant_id() -> uuid.UUID | None:
    return _current_tenant_id.get()


def set_current_tenant_id(tenant_id: uuid.UUID | None) -> None:
    _current_tenant_id.set(tenant_id)


_TENANT_MODELS: set[type] = set()


def register_tenant_model(model: type) -> None:
    _TENANT_MODELS.add(model)


@event.listens_for(Session, "do_orm_execute")
def _inject_tenant_filter(execute_state):
    tenant_id = _current_tenant_id.get()
    if tenant_id is None:
        return
    if not execute_state.is_orm_statement:
        return

    stmt = execute_state.statement
    for col_desc in stmt.column_descriptions:
        entity = col_desc.get("type")
        if entity is not None and hasattr(entity, "tenant_id"):
            stmt = stmt.options(
                with_loader_criteria(entity, entity.tenant_id == tenant_id)
            )
    execute_state.statement = stmt


@event.listens_for(Session, "before_flush")
def _set_tenant_on_insert(session, flush_context, instances):
    tenant_id = _current_tenant_id.get()
    if tenant_id is None:
        return
    for obj in session.new:
        if hasattr(obj, "tenant_id") and obj.tenant_id is None:
            obj.tenant_id = tenant_id
