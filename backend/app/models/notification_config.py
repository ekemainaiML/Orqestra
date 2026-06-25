import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import Base


class NotificationConfig(Base):
    __tablename__ = "notification_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    smtp_host: Mapped[str] = mapped_column(String(255), default="", server_default="")
    smtp_port: Mapped[int] = mapped_column(Integer, default=587, server_default="587")
    smtp_username: Mapped[str] = mapped_column(String(255), default="", server_default="")
    smtp_password: Mapped[str] = mapped_column(String(255), default="", server_default="")
    smtp_from: Mapped[str] = mapped_column(
        String(255), default="noreply@orqestra.ai", server_default="noreply@orqestra.ai"
    )
    slack_webhook_url: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
