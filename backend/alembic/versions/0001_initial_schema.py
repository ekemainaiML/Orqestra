"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2025-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("request_text", sa.Text, nullable=False),
        sa.Column("status", sa.Enum(
            "created", "memory_retrieval", "independent_assessment", "challenge_round",
            "consensus_scoring", "adjudication", "approval_pending", "clarification_required",
            "escalated", "rejected", "failed", "completed", "closed", "closed_without_resolution",
            "constraint_modified", "redeliberation_pending", name="case_status",
        ), default="created", nullable=False),
        sa.Column("iteration", sa.Integer, default=0, nullable=False),
        sa.Column("workflow_type", sa.String(64), default="order_fulfillment", nullable=False),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("completeness", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "workflow_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("iteration", sa.Integer, default=0, nullable=False),
        sa.Column("event_type", sa.Enum(
            "case_created", "memory_retrieved", "recommendation_submitted", "challenge_issued",
            "consensus_calculated", "decision_generated", "brief_presented", "decision_approved",
            "decision_rejected", "constraint_modified", "iteration_started", "workflow_completed",
            "agent_unavailable", "workflow_escalated", "clarification_requested", name="event_type",
        ), nullable=False),
        sa.Column("actor", sa.String(64), nullable=False),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "memories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("memory_type", sa.Enum("operational", "organizational", "department", name="memory_type"), nullable=False),
        sa.Column("domain", sa.Enum("customer", "supplier", "policy", "decision", name="memory_domain"), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column("importance", sa.Float, default=0.0, nullable=False),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("agent_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "directives",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("iteration", sa.Integer, default=0, nullable=False),
        sa.Column("directive_type", sa.String(64), nullable=False),
        sa.Column("value", JSONB, nullable=False),
        sa.Column("issued_by", sa.String(64), default="operator", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "benchmark_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("run_type", sa.Enum("single_agent", "organization", name="benchmark_run_type"), nullable=False),
        sa.Column("recommendation", JSONB, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("risks_found", sa.Integer, default=0, nullable=False),
        sa.Column("factors_considered", sa.Integer, default=0, nullable=False),
        sa.Column("reasoning_time_s", sa.Float, default=0.0, nullable=False),
        sa.Column("memory_used", sa.Integer, default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("benchmark_runs")
    op.drop_table("directives")
    op.drop_table("memories")
    op.drop_table("workflow_events")
    op.drop_table("cases")
    op.drop_table("customers")

    op.execute("DROP TYPE IF EXISTS benchmark_run_type")
    op.execute("DROP TYPE IF EXISTS memory_domain")
    op.execute("DROP TYPE IF EXISTS memory_type")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS case_status")
