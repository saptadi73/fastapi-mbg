"""add feedback foundation

Revision ID: 20260720_0715
Revises: 20260720_0705
Create Date: 2026-07-19 07:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0715"
down_revision: str | Sequence[str] | None = "20260720_0705"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback_submissions",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("meal_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feedback_date", sa.Date(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("respondent_name", sa.String(length=255), nullable=True),
        sa.Column("respondent_role", sa.String(length=100), nullable=True),
        sa.Column("overall_rating", sa.Float(), nullable=True),
        sa.Column("acceptance_rate", sa.Float(), nullable=True),
        sa.Column("food_waste_portions", sa.Float(), nullable=True),
        sa.Column("delivery_timeliness_rating", sa.Float(), nullable=True),
        sa.Column("temperature_rating", sa.Float(), nullable=True),
        sa.Column("comment_text", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="SUBMITTED"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["delivery_order_id"], ["delivery_orders.id"]),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"]),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_submissions_delivery_order_id"), "feedback_submissions", ["delivery_order_id"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_feedback_date"), "feedback_submissions", ["feedback_date"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_meal_plan_id"), "feedback_submissions", ["meal_plan_id"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_school_id"), "feedback_submissions", ["school_id"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_source_type"), "feedback_submissions", ["source_type"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_sppg_id"), "feedback_submissions", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_status"), "feedback_submissions", ["status"], unique=False)
    op.create_index(op.f("ix_feedback_submissions_tenant_id"), "feedback_submissions", ["tenant_id"], unique=False)

    op.create_table(
        "feedback_items",
        sa.Column("feedback_submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("sentiment", sa.String(length=50), nullable=True),
        sa.Column("comment_text", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["feedback_submission_id"], ["feedback_submissions.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_items_feedback_submission_id"), "feedback_items", ["feedback_submission_id"], unique=False)
    op.create_index(op.f("ix_feedback_items_item_type"), "feedback_items", ["item_type"], unique=False)
    op.create_index(op.f("ix_feedback_items_metric_name"), "feedback_items", ["metric_name"], unique=False)
    op.create_index(op.f("ix_feedback_items_tenant_id"), "feedback_items", ["tenant_id"], unique=False)

    op.create_table(
        "complaints",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feedback_submission_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("complaint_date", sa.DateTime(timezone=False), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("complaint_text", sa.String(length=2000), nullable=False),
        sa.Column("resolution_status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("resolved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["feedback_submission_id"], ["feedback_submissions.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_complaints_category"), "complaints", ["category"], unique=False)
    op.create_index(op.f("ix_complaints_complaint_date"), "complaints", ["complaint_date"], unique=False)
    op.create_index(op.f("ix_complaints_feedback_submission_id"), "complaints", ["feedback_submission_id"], unique=False)
    op.create_index(op.f("ix_complaints_resolution_status"), "complaints", ["resolution_status"], unique=False)
    op.create_index(op.f("ix_complaints_severity"), "complaints", ["severity"], unique=False)
    op.create_index(op.f("ix_complaints_sppg_id"), "complaints", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_complaints_tenant_id"), "complaints", ["tenant_id"], unique=False)

    op.create_table(
        "service_quality_scores",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score_date", sa.Date(), nullable=False),
        sa.Column("acceptance_score", sa.Float(), nullable=True),
        sa.Column("waste_score", sa.Float(), nullable=True),
        sa.Column("delivery_score", sa.Float(), nullable=True),
        sa.Column("temperature_score", sa.Float(), nullable=True),
        sa.Column("taste_score", sa.Float(), nullable=True),
        sa.Column("nutrition_score", sa.Float(), nullable=True),
        sa.Column("complaint_score", sa.Float(), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_status", sa.String(length=50), nullable=False, server_default="CALCULATED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "sppg_id", "score_date", name="uq_service_quality_scores_scope_date"),
    )
    op.create_index(op.f("ix_service_quality_scores_score_date"), "service_quality_scores", ["score_date"], unique=False)
    op.create_index(op.f("ix_service_quality_scores_score_status"), "service_quality_scores", ["score_status"], unique=False)
    op.create_index(op.f("ix_service_quality_scores_sppg_id"), "service_quality_scores", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_service_quality_scores_tenant_id"), "service_quality_scores", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_service_quality_scores_tenant_id"), table_name="service_quality_scores")
    op.drop_index(op.f("ix_service_quality_scores_sppg_id"), table_name="service_quality_scores")
    op.drop_index(op.f("ix_service_quality_scores_score_status"), table_name="service_quality_scores")
    op.drop_index(op.f("ix_service_quality_scores_score_date"), table_name="service_quality_scores")
    op.drop_table("service_quality_scores")
    op.drop_index(op.f("ix_complaints_tenant_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_sppg_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_severity"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_resolution_status"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_feedback_submission_id"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_complaint_date"), table_name="complaints")
    op.drop_index(op.f("ix_complaints_category"), table_name="complaints")
    op.drop_table("complaints")
    op.drop_index(op.f("ix_feedback_items_tenant_id"), table_name="feedback_items")
    op.drop_index(op.f("ix_feedback_items_metric_name"), table_name="feedback_items")
    op.drop_index(op.f("ix_feedback_items_item_type"), table_name="feedback_items")
    op.drop_index(op.f("ix_feedback_items_feedback_submission_id"), table_name="feedback_items")
    op.drop_table("feedback_items")
    op.drop_index(op.f("ix_feedback_submissions_tenant_id"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_status"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_sppg_id"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_source_type"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_school_id"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_meal_plan_id"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_feedback_date"), table_name="feedback_submissions")
    op.drop_index(op.f("ix_feedback_submissions_delivery_order_id"), table_name="feedback_submissions")
    op.drop_table("feedback_submissions")
