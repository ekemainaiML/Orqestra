import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import app
from app.models import Base
from app.models.benchmark_run import BenchmarkRun
from app.models.case import Case
from app.models.customer import Customer
from app.models.directive import Directive
from app.models.memory import Memory
from app.models.workflow_event import WorkflowEvent
from app.services.settings import settings

import os as _os

TEST_DB_URL = _os.environ.get("TEST_DATABASE_URL")
if not TEST_DB_URL:
    _base = settings.database_url
    if _os.environ.get("DATABASE_URL"):
        _base = _base
    else:
        _base = _base.replace("localhost:5432", "localhost:5433")
    _base = _base.replace("/orqestra", "/orqestra_test")
    TEST_DB_URL = _base

@pytest_asyncio.fixture
async def setup_database():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def seed_customers(db_session: AsyncSession) -> list[Customer]:
    customers = [
        Customer(
            id=uuid.UUID("a1b2c3d4-0001-4000-8000-000000000001"),
            name="Jane Greenfield",
            email="jane@greenfield.gov",
            company="Greenfield Municipal Council",
            notes="Government client — net-60 terms",
        ),
        Customer(
            id=uuid.UUID("a1b2c3d4-0002-4000-8000-000000000002"),
            name="Mark Sunlight",
            email="mark@sunlight.org",
            company="Sunlight Initiative",
            notes="NGO client — budget sensitive",
        ),
    ]
    for c in customers:
        db_session.add(c)
    await db_session.commit()
    return customers


@pytest_asyncio.fixture
async def seed_case(db_session: AsyncSession, seed_customers: list[Customer]) -> Case:
    case = Case(
        customer_id=seed_customers[0].id,
        request_text="Government order — 500 solar-powered street lights for municipal lighting project.",
        status="created",
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def _make_test_app():
    from fastapi import FastAPI

    test_app = FastAPI(title="Orqestra Test", version="0.1.0")
    from app.api import admin, benchmark, cases, dashboard, demo, events
    from app.auth.router import router as auth_router
    test_app.include_router(auth_router)
    test_app.include_router(admin.router)
    test_app.include_router(cases.router)
    test_app.include_router(demo.router)
    test_app.include_router(events.router)
    test_app.include_router(benchmark.router)
    test_app.include_router(dashboard.router)

    @test_app.get("/health")
    async def health():
        return {"status": "ok"}

    @test_app.get("/health/integrations")
    async def _integration_health():
        from app.services.settings import settings as _s
        return {
            k: {"configured": bool(v[0]), "status": "connected" if v[0] else "not_configured"}
            for k, v in {
                "hubspot": (_s.hubspot_api_key,),
                "odoo": (_s.odoo_url and _s.odoo_db,),
                "paystack": (_s.paystack_secret_key,),
                "dhl": (_s.dhl_api_key,),
                "qwen": (_s.dashscope_api_key,),
                "slack": (_s.slack_webhook_url,),
                "smtp": (_s.smtp_host,),
            }.items()
        }

    return test_app


@pytest_asyncio.fixture
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    from app.services.database import get_session

    engine = create_async_engine(TEST_DB_URL, echo=False)

    async def override_get_session():
        session = AsyncSession(engine, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()

    test_app = _make_test_app()
    test_app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await engine.dispose()


@pytest.fixture
def sample_recommendations() -> list[dict]:
    return [
        {
            "agent_id": "sales",
            "recommendation": "Proceed with order for 500 units. Customer is a repeat government client.",
            "reasoning": "Strong customer relationship and clear requirements.",
            "confidence": 0.85,
            "risks": ["No significant risks identified"],
            "alternatives": [],
            "evidence": [],
        },
        {
            "agent_id": "finance",
            "recommendation": "Budget approved at $83,362 with 28% margin. Government net-60 terms apply.",
            "reasoning": "Margin within acceptable range. Government client reduces payment risk.",
            "confidence": 0.78,
            "risks": ["Net-60 payment terms may impact cash flow"],
            "alternatives": [],
            "evidence": [],
        },
        {
            "agent_id": "inventory",
            "recommendation": "Stock check: 150 available, 350 shortfall. Procurement required.",
            "reasoning": "Current stock insufficient for 500 units. Need supplier sourcing.",
            "confidence": 0.65,
            "risks": ["Shortfall of 350 units", "Potential production delay"],
            "alternatives": [],
            "evidence": [],
        },
    ]
