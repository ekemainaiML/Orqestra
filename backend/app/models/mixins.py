import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TenantMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID | None]:  # noqa: N805
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        )
