"""add goods receipts"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260720_0015"
down_revision = "20260719_2345"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "goods_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_number", sa.String(length=50), nullable=False),
        sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'POSTED'")),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["purchase_request_id"], ["purchase_requests.id"], name=op.f("fk_goods_receipts_purchase_request_id_purchase_requests")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_goods_receipts_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_goods_receipts_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], name=op.f("fk_goods_receipts_warehouse_id_warehouses")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_goods_receipts")),
        sa.UniqueConstraint("tenant_id", "receipt_number", name="uq_goods_receipts_tenant_receipt_number"),
    )
    op.create_index("ix_goods_receipts_purchase_request_id", "goods_receipts", ["purchase_request_id"], unique=False)
    op.create_index("ix_goods_receipts_receipt_number", "goods_receipts", ["receipt_number"], unique=False)
    op.create_index("ix_goods_receipts_sppg_id", "goods_receipts", ["sppg_id"], unique=False)
    op.create_index("ix_goods_receipts_tenant_id", "goods_receipts", ["tenant_id"], unique=False)

    op.create_table(
        "goods_receipt_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goods_receipt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_request_line_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("received_quantity", sa.Float(), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["goods_receipt_id"], ["goods_receipts.id"], name=op.f("fk_goods_receipt_lines_goods_receipt_id_goods_receipts")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_goods_receipt_lines_product_id_products")),
        sa.ForeignKeyConstraint(["purchase_request_line_id"], ["purchase_request_lines.id"], name=op.f("fk_goods_receipt_lines_purchase_request_line_id_purchase_request_lines")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_goods_receipt_lines_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_goods_receipt_lines_uom_id_uoms")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_goods_receipt_lines")),
    )
    op.create_index("ix_goods_receipt_lines_goods_receipt_id", "goods_receipt_lines", ["goods_receipt_id"], unique=False)
    op.create_index("ix_goods_receipt_lines_product_id", "goods_receipt_lines", ["product_id"], unique=False)
    op.create_index("ix_goods_receipt_lines_tenant_id", "goods_receipt_lines", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_goods_receipt_lines_tenant_id", table_name="goods_receipt_lines")
    op.drop_index("ix_goods_receipt_lines_product_id", table_name="goods_receipt_lines")
    op.drop_index("ix_goods_receipt_lines_goods_receipt_id", table_name="goods_receipt_lines")
    op.drop_table("goods_receipt_lines")

    op.drop_index("ix_goods_receipts_tenant_id", table_name="goods_receipts")
    op.drop_index("ix_goods_receipts_sppg_id", table_name="goods_receipts")
    op.drop_index("ix_goods_receipts_receipt_number", table_name="goods_receipts")
    op.drop_index("ix_goods_receipts_purchase_request_id", table_name="goods_receipts")
    op.drop_table("goods_receipts")
