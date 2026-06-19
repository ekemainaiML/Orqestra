import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_type: Mapped[str] = mapped_column(
        Enum("operational", "organizational", "department", name="memory_type"),
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        Enum("customer", "supplier", "policy", "decision", name="memory_domain"),
        nullable=False,
    )
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    department: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "memory_type": self.memory_type,
            "domain": self.domain,
            "entity_id": self.entity_id,
            "content": self.content,
            "importance": self.importance,
            "department": self.department,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
