"""add platform ops outbox read models

Revision ID: 20260720_1115
Revises: 20260720_1045
Create Date: 2026-07-20 11:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_1115"
down_revision: str | Sequence[str] | None = "20260720_1045"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "outbox_events",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_name", sa.String(length=150), nullable=False),
        sa.Column("aggregate_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_error", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_events_tenant_id", "outbox_events", ["tenant_id"], unique=False)
    op.create_index("ix_outbox_events_event_name", "outbox_events", ["event_name"], unique=False)
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"], unique=False)
    op.create_index("ix_outbox_events_status", "outbox_events", ["status"], unique=False)

    op.create_table(
        "background_jobs",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_name", sa.String(length=150), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "job_name", name="uq_background_jobs_tenant_job_name"),
    )
    op.create_index("ix_background_jobs_tenant_id", "background_jobs", ["tenant_id"], unique=False)
    op.create_index("ix_background_jobs_job_type", "background_jobs", ["job_type"], unique=False)

    op.create_table(
        "daily_kitchen_operation_summaries",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary_date", sa.Date(), nullable=False),
        sa.Column("meal_plan_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("production_order_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("delivery_order_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("accepted_portions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("delivered_portions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("rejected_portions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("labor_cost_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("refresh_source", sa.String(length=50), nullable=False, server_default="SUMMARY_TABLE"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "sppg_id", "summary_date", name="uq_daily_kitchen_operation_scope_date"),
    )
    op.create_index("ix_daily_kitchen_operation_summaries_tenant_id", "daily_kitchen_operation_summaries", ["tenant_id"], unique=False)
    op.create_index("ix_daily_kitchen_operation_summaries_sppg_id", "daily_kitchen_operation_summaries", ["sppg_id"], unique=False)
    op.create_index("ix_daily_kitchen_operation_summaries_summary_date", "daily_kitchen_operation_summaries", ["summary_date"], unique=False)

    op.create_table(
        "monthly_budget_realization_summaries",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column("budgets_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("effective_budget", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("reserved_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("committed_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("actual_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("refresh_source", sa.String(length=50), nullable=False, server_default="SUMMARY_TABLE"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "period_month", name="uq_monthly_budget_realization_tenant_month"),
    )
    op.create_index("ix_monthly_budget_realization_summaries_tenant_id", "monthly_budget_realization_summaries", ["tenant_id"], unique=False)
    op.create_index("ix_monthly_budget_realization_summaries_period_month", "monthly_budget_realization_summaries", ["period_month"], unique=False)

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_delivery_performance_summary AS
        SELECT
            tenant_id,
            sppg_id,
            status,
            COUNT(*) AS delivery_orders,
            COALESCE(SUM(shipped_portions), 0) AS shipped_portions,
            COALESCE(SUM(received_portions), 0) AS received_portions,
            COALESCE(SUM(rejected_portions), 0) AS rejected_portions
        FROM delivery_orders
        GROUP BY tenant_id, sppg_id, status
        """
    )
    op.execute("CREATE UNIQUE INDEX ux_mv_delivery_performance_summary_scope ON mv_delivery_performance_summary (tenant_id, sppg_id, status)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_mv_delivery_performance_summary_scope")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_delivery_performance_summary")

    op.drop_index("ix_monthly_budget_realization_summaries_period_month", table_name="monthly_budget_realization_summaries")
    op.drop_index("ix_monthly_budget_realization_summaries_tenant_id", table_name="monthly_budget_realization_summaries")
    op.drop_table("monthly_budget_realization_summaries")

    op.drop_index("ix_daily_kitchen_operation_summaries_summary_date", table_name="daily_kitchen_operation_summaries")
    op.drop_index("ix_daily_kitchen_operation_summaries_sppg_id", table_name="daily_kitchen_operation_summaries")
    op.drop_index("ix_daily_kitchen_operation_summaries_tenant_id", table_name="daily_kitchen_operation_summaries")
    op.drop_table("daily_kitchen_operation_summaries")

    op.drop_index("ix_background_jobs_job_type", table_name="background_jobs")
    op.drop_index("ix_background_jobs_tenant_id", table_name="background_jobs")
    op.drop_table("background_jobs")

    op.drop_index("ix_outbox_events_status", table_name="outbox_events")
    op.drop_index("ix_outbox_events_aggregate_id", table_name="outbox_events")
    op.drop_index("ix_outbox_events_event_name", table_name="outbox_events")
    op.drop_index("ix_outbox_events_tenant_id", table_name="outbox_events")
    op.drop_table("outbox_events")
