import os
from contextlib import asynccontextmanager

import sqlalchemy as sa
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api import admin, benchmark, cases, dashboard, demo, events
from app.auth.middleware import AuthMiddleware
from app.auth.router import _hash_password, router as auth_router
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.models import Base, UserModel, WorkflowConfigModel
from app.services.database import get_async_session, get_engine
from app.services.logging import RequestLoggingMiddleware, setup_logging
from app.services.metrics import metrics
from app.services.settings import settings

WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), "workflows")


COLUMN_TYPE_MIGRATIONS = [
    (
        "workflow_events",
        "event_type",
        "event_type",
        "VARCHAR(64)",
    ),
]


async def _migrate_enum_columns():
    """Convert PG ENUM columns to VARCHAR so new values can be added without ALTER TYPE."""
    async with get_engine().begin() as conn:
        for table, column, enum_name, target_type in COLUMN_TYPE_MIGRATIONS:
            row = await conn.execute(
                sa.text(
                    "SELECT data_type FROM information_schema.columns "
                    "WHERE table_name = :table AND column_name = :column"
                ),
                {"table": table, "column": column},
            )
            result = row.scalar()
            if result == "USER-DEFINED":
                await conn.execute(
                    sa.text(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {target_type} USING {column}::text")
                )
                await conn.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name}"))
                print(f"  ✓ Migrated {table}.{column} from ENUM to {target_type}, dropped type '{enum_name}'")


async def _seed_workflow_configs():
    async with get_async_session()() as session:
        for fname in sorted(f for f in os.listdir(WORKFLOWS_DIR) if f.endswith(".yaml") and f != "__init__.yaml"):
            config_id = fname.removesuffix(".yaml")
            existing = await session.scalar(select(WorkflowConfigModel).where(WorkflowConfigModel.id == config_id))
            if existing:
                continue
            filepath = os.path.join(WORKFLOWS_DIR, fname)
            with open(filepath) as f:
                yaml_content = f.read()
            data = yaml.safe_load(yaml_content)
            name = data.get("name", config_id.replace("_", " ").title())
            session.add(WorkflowConfigModel(id=config_id, name=name, yaml_content=yaml_content, is_builtin=True))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.environment)
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_enum_columns()
    async with get_async_session()() as session:
        existing = await session.scalar(select(UserModel).limit(1))
        if existing is None:
            session.add(
                UserModel(
                    username=settings.auth_username,
                    password_hash=_hash_password(settings.auth_password),
                )
            )
            await session.commit()
            print(f"  ✓ Seeded default user '{settings.auth_username}'")
    await _seed_workflow_configs()
    yield
    await get_engine().dispose()


app = FastAPI(title="Orqestra", version="0.1.0", lifespan=lifespan)

_cors_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.cors_origins:
    _cors_origins.extend([o.strip() for o in settings.cors_origins.split(",") if o.strip()])
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(admin.router)
app.include_router(cases.router)
app.include_router(demo.router)
app.include_router(events.router)
app.include_router(benchmark.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health():
    db_ok = False
    try:
        async with get_engine().connect() as conn:
            await conn.execute(sa.text("SELECT 1"))
            db_ok = True
    except Exception:
        pass
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "orqestra",
        "environment": settings.environment,
        "database": "connected" if db_ok else "unreachable",
    }


@app.get("/metrics")
async def get_metrics():
    return metrics.snapshot()
