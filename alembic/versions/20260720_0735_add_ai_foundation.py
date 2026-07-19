"""add ai foundation

Revision ID: 20260720_0735
Revises: 20260720_0725
Create Date: 2026-07-19 07:35:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0735"
down_revision: str | Sequence[str] | None = "20260720_0725"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_forecasts",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("forecast_type", sa.String(length=100), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("forecast_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="GENERATED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_forecasts_forecast_date"), "ai_forecasts", ["forecast_date"], unique=False)
    op.create_index(op.f("ix_ai_forecasts_forecast_type"), "ai_forecasts", ["forecast_type"], unique=False)
    op.create_index(op.f("ix_ai_forecasts_sppg_id"), "ai_forecasts", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_ai_forecasts_status"), "ai_forecasts", ["status"], unique=False)
    op.create_index(op.f("ix_ai_forecasts_target_date"), "ai_forecasts", ["target_date"], unique=False)
    op.create_index(op.f("ix_ai_forecasts_tenant_id"), "ai_forecasts", ["tenant_id"], unique=False)

    op.create_table(
        "ai_recommendations",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recommendation_date", sa.Date(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=100), nullable=False),
        sa.Column("reference_type", sa.String(length=100), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary_text", sa.String(length=2000), nullable=False),
        sa.Column("recommendation_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_recommendations_priority"), "ai_recommendations", ["priority"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_recommendation_date"), "ai_recommendations", ["recommendation_date"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_recommendation_type"), "ai_recommendations", ["recommendation_type"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_reference_id"), "ai_recommendations", ["reference_id"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_sppg_id"), "ai_recommendations", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_status"), "ai_recommendations", ["status"], unique=False)
    op.create_index(op.f("ix_ai_recommendations_tenant_id"), "ai_recommendations", ["tenant_id"], unique=False)

    op.create_table(
        "ai_daily_summaries",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary_date", sa.Date(), nullable=False),
        sa.Column("summary_type", sa.String(length=100), nullable=False, server_default="OPERATIONS"),
        sa.Column("headline", sa.String(length=255), nullable=False),
        sa.Column("summary_text", sa.String(length=4000), nullable=False),
        sa.Column("metrics_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("anomaly_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recommendation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="GENERATED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "sppg_id", "summary_date", name="uq_ai_daily_summary_scope_date"),
    )
    op.create_index(op.f("ix_ai_daily_summaries_sppg_id"), "ai_daily_summaries", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_ai_daily_summaries_status"), "ai_daily_summaries", ["status"], unique=False)
    op.create_index(op.f("ix_ai_daily_summaries_summary_date"), "ai_daily_summaries", ["summary_date"], unique=False)
    op.create_index(op.f("ix_ai_daily_summaries_summary_type"), "ai_daily_summaries", ["summary_type"], unique=False)
    op.create_index(op.f("ix_ai_daily_summaries_tenant_id"), "ai_daily_summaries", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_daily_summaries_tenant_id"), table_name="ai_daily_summaries")
    op.drop_index(op.f("ix_ai_daily_summaries_summary_type"), table_name="ai_daily_summaries")
    op.drop_index(op.f("ix_ai_daily_summaries_summary_date"), table_name="ai_daily_summaries")
    op.drop_index(op.f("ix_ai_daily_summaries_status"), table_name="ai_daily_summaries")
    op.drop_index(op.f("ix_ai_daily_summaries_sppg_id"), table_name="ai_daily_summaries")
    op.drop_table("ai_daily_summaries")
    op.drop_index(op.f("ix_ai_recommendations_tenant_id"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_status"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_sppg_id"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_reference_id"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_recommendation_type"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_recommendation_date"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_priority"), table_name="ai_recommendations")
    op.drop_table("ai_recommendations")
    op.drop_index(op.f("ix_ai_forecasts_tenant_id"), table_name="ai_forecasts")
    op.drop_index(op.f("ix_ai_forecasts_target_date"), table_name="ai_forecasts")
    op.drop_index(op.f("ix_ai_forecasts_status"), table_name="ai_forecasts")
    op.drop_index(op.f("ix_ai_forecasts_sppg_id"), table_name="ai_forecasts")
    op.drop_index(op.f("ix_ai_forecasts_forecast_type"), table_name="ai_forecasts")
    op.drop_index(op.f("ix_ai_forecasts_forecast_date"), table_name="ai_forecasts")
    op.drop_table("ai_forecasts")
