"""add supplier invoices

Revision ID: 20260720_0415
Revises: 20260720_0330
Create Date: 2026-07-20 04:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260720_0415"
down_revision: str | None = "20260720_0330"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "supplier_invoices",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goods_receipt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["budget_account_id"], ["accounts.id"], name=op.f("fk_supplier_invoices_budget_account_id_accounts")),
        sa.ForeignKeyConstraint(["goods_receipt_id"], ["goods_receipts.id"], name=op.f("fk_supplier_invoices_goods_receipt_id_goods_receipts")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_supplier_invoices_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_supplier_invoices_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_supplier_invoices")),
        sa.UniqueConstraint("tenant_id", "invoice_number", name="uq_supplier_invoices_tenant_invoice_number"),
    )
    op.create_index(op.f("ix_supplier_invoices_goods_receipt_id"), "supplier_invoices", ["goods_receipt_id"], unique=False)
    op.create_index(op.f("ix_supplier_invoices_invoice_number"), "supplier_invoices", ["invoice_number"], unique=False)
    op.create_index(op.f("ix_supplier_invoices_sppg_id"), "supplier_invoices", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_supplier_invoices_tenant_id"), "supplier_invoices", ["tenant_id"], unique=False)

    op.create_table(
        "supplier_invoice_lines",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goods_receipt_line_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoiced_quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["goods_receipt_line_id"], ["goods_receipt_lines.id"], name=op.f("fk_supplier_invoice_lines_goods_receipt_line_id_goods_receipt_lines")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_supplier_invoice_lines_product_id_products")),
        sa.ForeignKeyConstraint(["supplier_invoice_id"], ["supplier_invoices.id"], name=op.f("fk_supplier_invoice_lines_supplier_invoice_id_supplier_invoices")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_supplier_invoice_lines_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_supplier_invoice_lines_uom_id_uoms")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_supplier_invoice_lines")),
    )
    op.create_index(op.f("ix_supplier_invoice_lines_goods_receipt_line_id"), "supplier_invoice_lines", ["goods_receipt_line_id"], unique=False)
    op.create_index(op.f("ix_supplier_invoice_lines_product_id"), "supplier_invoice_lines", ["product_id"], unique=False)
    op.create_index(op.f("ix_supplier_invoice_lines_supplier_invoice_id"), "supplier_invoice_lines", ["supplier_invoice_id"], unique=False)
    op.create_index(op.f("ix_supplier_invoice_lines_tenant_id"), "supplier_invoice_lines", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_supplier_invoice_lines_tenant_id"), table_name="supplier_invoice_lines")
    op.drop_index(op.f("ix_supplier_invoice_lines_supplier_invoice_id"), table_name="supplier_invoice_lines")
    op.drop_index(op.f("ix_supplier_invoice_lines_product_id"), table_name="supplier_invoice_lines")
    op.drop_index(op.f("ix_supplier_invoice_lines_goods_receipt_line_id"), table_name="supplier_invoice_lines")
    op.drop_table("supplier_invoice_lines")

    op.drop_index(op.f("ix_supplier_invoices_tenant_id"), table_name="supplier_invoices")
    op.drop_index(op.f("ix_supplier_invoices_sppg_id"), table_name="supplier_invoices")
    op.drop_index(op.f("ix_supplier_invoices_invoice_number"), table_name="supplier_invoices")
    op.drop_index(op.f("ix_supplier_invoices_goods_receipt_id"), table_name="supplier_invoices")
    op.drop_table("supplier_invoices")
