"""add funding foundation

Revision ID: 20260720_0655
Revises: 20260720_0645
Create Date: 2026-07-19 06:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0655"
down_revision: str | Sequence[str] | None = "20260720_0645"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "funding_sources",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("party_name", sa.String(length=255), nullable=True),
        sa.Column("contract_number", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_funding_sources_tenant_code"),
    )
    op.create_index(op.f("ix_funding_sources_code"), "funding_sources", ["code"], unique=False)
    op.create_index(op.f("ix_funding_sources_source_type"), "funding_sources", ["source_type"], unique=False)
    op.create_index(op.f("ix_funding_sources_status"), "funding_sources", ["status"], unique=False)
    op.create_index(op.f("ix_funding_sources_tenant_id"), "funding_sources", ["tenant_id"], unique=False)

    op.create_table(
        "funding_agreements",
        sa.Column("funding_source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agreement_type", sa.String(length=100), nullable=False),
        sa.Column("principal_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("margin_method", sa.String(length=100), nullable=True),
        sa.Column("margin_rate", sa.Float(), nullable=True),
        sa.Column("fixed_margin_amount", sa.Float(), nullable=True),
        sa.Column("disbursement_schedule", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("repayment_terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["funding_source_id"], ["funding_sources.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_funding_agreements_agreement_type"), "funding_agreements", ["agreement_type"], unique=False)
    op.create_index(op.f("ix_funding_agreements_funding_source_id"), "funding_agreements", ["funding_source_id"], unique=False)
    op.create_index(op.f("ix_funding_agreements_status"), "funding_agreements", ["status"], unique=False)
    op.create_index(op.f("ix_funding_agreements_tenant_id"), "funding_agreements", ["tenant_id"], unique=False)

    op.create_table(
        "funding_disbursements",
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("disbursement_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_number", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="POSTED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agreement_id"], ["funding_agreements.id"]),
        sa.ForeignKeyConstraint(["bank_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_funding_disbursements_agreement_id"), "funding_disbursements", ["agreement_id"], unique=False)
    op.create_index(op.f("ix_funding_disbursements_bank_account_id"), "funding_disbursements", ["bank_account_id"], unique=False)
    op.create_index(op.f("ix_funding_disbursements_journal_entry_id"), "funding_disbursements", ["journal_entry_id"], unique=False)
    op.create_index(op.f("ix_funding_disbursements_sppg_id"), "funding_disbursements", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_funding_disbursements_status"), "funding_disbursements", ["status"], unique=False)
    op.create_index(op.f("ix_funding_disbursements_tenant_id"), "funding_disbursements", ["tenant_id"], unique=False)

    op.create_table(
        "funding_repayments",
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("repayment_date", sa.Date(), nullable=False),
        sa.Column("principal_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("margin_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("penalty_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("payment_reference", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="POSTED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agreement_id"], ["funding_agreements.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_funding_repayments_agreement_id"), "funding_repayments", ["agreement_id"], unique=False)
    op.create_index(op.f("ix_funding_repayments_journal_entry_id"), "funding_repayments", ["journal_entry_id"], unique=False)
    op.create_index(op.f("ix_funding_repayments_status"), "funding_repayments", ["status"], unique=False)
    op.create_index(op.f("ix_funding_repayments_tenant_id"), "funding_repayments", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_funding_repayments_tenant_id"), table_name="funding_repayments")
    op.drop_index(op.f("ix_funding_repayments_status"), table_name="funding_repayments")
    op.drop_index(op.f("ix_funding_repayments_journal_entry_id"), table_name="funding_repayments")
    op.drop_index(op.f("ix_funding_repayments_agreement_id"), table_name="funding_repayments")
    op.drop_table("funding_repayments")
    op.drop_index(op.f("ix_funding_disbursements_tenant_id"), table_name="funding_disbursements")
    op.drop_index(op.f("ix_funding_disbursements_status"), table_name="funding_disbursements")
    op.drop_index(op.f("ix_funding_disbursements_sppg_id"), table_name="funding_disbursements")
    op.drop_index(op.f("ix_funding_disbursements_journal_entry_id"), table_name="funding_disbursements")
    op.drop_index(op.f("ix_funding_disbursements_bank_account_id"), table_name="funding_disbursements")
    op.drop_index(op.f("ix_funding_disbursements_agreement_id"), table_name="funding_disbursements")
    op.drop_table("funding_disbursements")
    op.drop_index(op.f("ix_funding_agreements_tenant_id"), table_name="funding_agreements")
    op.drop_index(op.f("ix_funding_agreements_status"), table_name="funding_agreements")
    op.drop_index(op.f("ix_funding_agreements_funding_source_id"), table_name="funding_agreements")
    op.drop_index(op.f("ix_funding_agreements_agreement_type"), table_name="funding_agreements")
    op.drop_table("funding_agreements")
    op.drop_index(op.f("ix_funding_sources_tenant_id"), table_name="funding_sources")
    op.drop_index(op.f("ix_funding_sources_status"), table_name="funding_sources")
    op.drop_index(op.f("ix_funding_sources_source_type"), table_name="funding_sources")
    op.drop_index(op.f("ix_funding_sources_code"), table_name="funding_sources")
    op.drop_table("funding_sources")
