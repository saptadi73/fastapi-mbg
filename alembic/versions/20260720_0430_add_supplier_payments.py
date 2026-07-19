"""add supplier payments

Revision ID: 20260720_0430
Revises: 20260720_0420
Create Date: 2026-07-20 04:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0430"
down_revision: str | None = "20260720_0420"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "supplier_payments",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["bank_account_id"], ["accounts.id"], name=op.f("fk_supplier_payments_bank_account_id_accounts")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_supplier_payments_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["supplier_invoice_id"], ["supplier_invoices.id"], name=op.f("fk_supplier_payments_supplier_invoice_id_supplier_invoices")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_supplier_payments_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_supplier_payments")),
        sa.UniqueConstraint("tenant_id", "payment_number", name="uq_supplier_payments_tenant_payment_number"),
    )
    op.create_index(op.f("ix_supplier_payments_payment_number"), "supplier_payments", ["payment_number"], unique=False)
    op.create_index(op.f("ix_supplier_payments_supplier_invoice_id"), "supplier_payments", ["supplier_invoice_id"], unique=False)
    op.create_index(op.f("ix_supplier_payments_sppg_id"), "supplier_payments", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_supplier_payments_tenant_id"), "supplier_payments", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_supplier_payments_tenant_id"), table_name="supplier_payments")
    op.drop_index(op.f("ix_supplier_payments_sppg_id"), table_name="supplier_payments")
    op.drop_index(op.f("ix_supplier_payments_supplier_invoice_id"), table_name="supplier_payments")
    op.drop_index(op.f("ix_supplier_payments_payment_number"), table_name="supplier_payments")
    op.drop_table("supplier_payments")
