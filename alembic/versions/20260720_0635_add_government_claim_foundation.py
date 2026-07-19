"""add government claim foundation

Revision ID: 20260720_0635
Revises: 20260720_0625
Create Date: 2026-07-19 06:35:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0635"
down_revision: str | Sequence[str] | None = "20260720_0625"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "government_claims",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("claim_number", sa.String(length=100), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("claim_type", sa.String(length=50), nullable=False, server_default="ACTUAL_COST"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("total_portions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("claimed_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("approved_amount", sa.Float(), nullable=True),
        sa.Column("paid_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("submitted_at", sa.Date(), nullable=True),
        sa.Column("verified_at", sa.Date(), nullable=True),
        sa.Column("paid_at", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "claim_number", name="uq_government_claims_tenant_claim_number"),
    )
    op.create_index(op.f("ix_government_claims_claim_number"), "government_claims", ["claim_number"], unique=False)
    op.create_index(op.f("ix_government_claims_program_id"), "government_claims", ["program_id"], unique=False)
    op.create_index(op.f("ix_government_claims_sppg_id"), "government_claims", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_government_claims_status"), "government_claims", ["status"], unique=False)
    op.create_index(op.f("ix_government_claims_tenant_id"), "government_claims", ["tenant_id"], unique=False)

    op.create_table(
        "government_claim_lines",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("line_type", sa.String(length=50), nullable=False, server_default="DELIVERY_ACTUAL_COST"),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("portions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("line_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["government_claims.id"]),
        sa.ForeignKeyConstraint(["delivery_order_id"], ["delivery_orders.id"]),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_government_claim_lines_claim_id"), "government_claim_lines", ["claim_id"], unique=False)
    op.create_index(op.f("ix_government_claim_lines_delivery_order_id"), "government_claim_lines", ["delivery_order_id"], unique=False)
    op.create_index(op.f("ix_government_claim_lines_production_order_id"), "government_claim_lines", ["production_order_id"], unique=False)
    op.create_index(op.f("ix_government_claim_lines_tenant_id"), "government_claim_lines", ["tenant_id"], unique=False)

    op.create_table(
        "claim_evidences",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_type", sa.String(length=100), nullable=False, server_default="SUPPORTING_DOCUMENT"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["government_claims.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_claim_evidences_claim_id"), "claim_evidences", ["claim_id"], unique=False)
    op.create_index(op.f("ix_claim_evidences_document_id"), "claim_evidences", ["document_id"], unique=False)
    op.create_index(op.f("ix_claim_evidences_tenant_id"), "claim_evidences", ["tenant_id"], unique=False)

    op.create_table(
        "claim_verifications",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verification_date", sa.Date(), nullable=False),
        sa.Column("verification_status", sa.String(length=50), nullable=False),
        sa.Column("verified_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("verifier_name", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["government_claims.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_claim_verifications_claim_id"), "claim_verifications", ["claim_id"], unique=False)
    op.create_index(op.f("ix_claim_verifications_tenant_id"), "claim_verifications", ["tenant_id"], unique=False)

    op.create_table(
        "claim_adjustments",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("adjustment_date", sa.Date(), nullable=False),
        sa.Column("adjustment_amount", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["government_claims.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_claim_adjustments_claim_id"), "claim_adjustments", ["claim_id"], unique=False)
    op.create_index(op.f("ix_claim_adjustments_tenant_id"), "claim_adjustments", ["tenant_id"], unique=False)

    op.create_table(
        "claim_payments",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_reference", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["government_claims.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_claim_payments_claim_id"), "claim_payments", ["claim_id"], unique=False)
    op.create_index(op.f("ix_claim_payments_journal_entry_id"), "claim_payments", ["journal_entry_id"], unique=False)
    op.create_index(op.f("ix_claim_payments_tenant_id"), "claim_payments", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_claim_payments_tenant_id"), table_name="claim_payments")
    op.drop_index(op.f("ix_claim_payments_journal_entry_id"), table_name="claim_payments")
    op.drop_index(op.f("ix_claim_payments_claim_id"), table_name="claim_payments")
    op.drop_table("claim_payments")
    op.drop_index(op.f("ix_claim_adjustments_tenant_id"), table_name="claim_adjustments")
    op.drop_index(op.f("ix_claim_adjustments_claim_id"), table_name="claim_adjustments")
    op.drop_table("claim_adjustments")
    op.drop_index(op.f("ix_claim_verifications_tenant_id"), table_name="claim_verifications")
    op.drop_index(op.f("ix_claim_verifications_claim_id"), table_name="claim_verifications")
    op.drop_table("claim_verifications")
    op.drop_index(op.f("ix_claim_evidences_tenant_id"), table_name="claim_evidences")
    op.drop_index(op.f("ix_claim_evidences_document_id"), table_name="claim_evidences")
    op.drop_index(op.f("ix_claim_evidences_claim_id"), table_name="claim_evidences")
    op.drop_table("claim_evidences")
    op.drop_index(op.f("ix_government_claim_lines_tenant_id"), table_name="government_claim_lines")
    op.drop_index(op.f("ix_government_claim_lines_production_order_id"), table_name="government_claim_lines")
    op.drop_index(op.f("ix_government_claim_lines_delivery_order_id"), table_name="government_claim_lines")
    op.drop_index(op.f("ix_government_claim_lines_claim_id"), table_name="government_claim_lines")
    op.drop_table("government_claim_lines")
    op.drop_index(op.f("ix_government_claims_tenant_id"), table_name="government_claims")
    op.drop_index(op.f("ix_government_claims_status"), table_name="government_claims")
    op.drop_index(op.f("ix_government_claims_sppg_id"), table_name="government_claims")
    op.drop_index(op.f("ix_government_claims_program_id"), table_name="government_claims")
    op.drop_index(op.f("ix_government_claims_claim_number"), table_name="government_claims")
    op.drop_table("government_claims")
