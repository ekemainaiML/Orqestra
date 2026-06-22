"""migrate event_type from ENUM to VARCHAR

Revision ID: 0002
Revises: 0001
Create Date: 2025-06-21
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE workflow_events ALTER COLUMN event_type TYPE VARCHAR(64) USING event_type::text"
    )
    op.execute("DROP TYPE IF EXISTS event_type")


def downgrade() -> None:
    op.execute("CREATE TYPE event_type AS ENUM (")
    op.execute(
        "'case_created', 'memory_retrieved', 'recommendation_submitted', 'challenge_issued', "
        "'consensus_calculated', 'decision_generated', 'brief_presented', 'decision_approved', "
        "'decision_rejected', 'constraint_modified', 'iteration_started', 'workflow_completed', "
        "'agent_unavailable', 'workflow_escalated', 'clarification_requested', 'tier_escalation'"
    )
    op.execute(")")
    op.execute(
        "ALTER TABLE workflow_events ALTER COLUMN event_type TYPE event_type USING event_type::text"
    )
