"""add tenant support

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-22 18:00:00.000000

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.execute(sa.text(
        "CREATE TABLE IF NOT EXISTS tenants ("
        "id UUID PRIMARY KEY, "
        "name VARCHAR(255) NOT NULL, "
        "slug VARCHAR(128) NOT NULL UNIQUE, "
        "settings TEXT, "
        "created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL"
        ")"
    ))
    op.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants (slug)"
    ))

    for table in ("customers", "users", "cases", "workflow_events", "directives",
                  "memories", "benchmark_runs", "workflow_configs"):
        op.execute(sa.text(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
            f"tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE"
        ))
        op.execute(sa.text(
            f"CREATE INDEX IF NOT EXISTS ix_{table}_tenant_id ON {table} (tenant_id)"
        ))


def downgrade():
    for table in ("customers", "users", "cases", "workflow_events", "directives",
                  "memories", "benchmark_runs", "workflow_configs"):
        op.execute(sa.text(f"DROP INDEX IF EXISTS ix_{table}_tenant_id"))
        op.execute(sa.text(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id"))
    op.execute(sa.text("DROP TABLE IF EXISTS tenants"))
