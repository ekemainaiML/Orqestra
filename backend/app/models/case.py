import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    request_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "created", "memory_retrieval", "independent_assessment", "challenge_round",
            "consensus_scoring", "adjudication", "approval_pending", "clarification_required",
            "escalated", "rejected", "failed", "completed", "closed", "closed_without_resolution",
            "constraint_modified", "redeliberation_pending", name="case_status",
        ),
        default="created",
        nullable=False,
    )
    iteration: Mapped[int] = mapped_column(default=0, nullable=False)
    workflow_type: Mapped[str] = mapped_column(String(64), default="order_fulfillment", nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    completeness: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    events = relationship("WorkflowEvent", back_populates="case", lazy="selectin")
    directives = relationship("Directive", back_populates="case", lazy="selectin")
