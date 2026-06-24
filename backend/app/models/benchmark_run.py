import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import TenantMixin
from app.services.database import Base


class BenchmarkRun(TenantMixin, Base):
    __tablename__ = "benchmark_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    run_type: Mapped[str] = mapped_column(
        Enum("single_agent", "organization", name="benchmark_run_type"),
        nullable=False,
    )
    recommendation: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risks_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    factors_considered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reasoning_time_s: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    memory_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
