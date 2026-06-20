from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import benchmark, cases, dashboard, demo, events
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.models import Base
from app.services.database import engine
from app.services.logging import RequestLoggingMiddleware, setup_logging
from app.services.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.environment)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Orqestra", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(cases.router)
app.include_router(demo.router)
app.include_router(events.router)
app.include_router(benchmark.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "orqestra", "environment": settings.environment}
