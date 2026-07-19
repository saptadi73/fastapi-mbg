"""expand procurement inventory foundation

Revision ID: 20260720_0905
Revises: 20260720_0815
Create Date: 2026-07-20 09:05:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0905"
down_revision: str | Sequence[str] | None = "20260720_0815"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("track_batch", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("products", sa.Column("track_expiry", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("products", sa.Column("minimum_stock", sa.Float(), nullable=False, server_default=sa.text("0")))
    op.add_column("products", sa.Column("maximum_stock", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("reorder_point", sa.Float(), nullable=False, server_default=sa.text("0")))
    op.add_column("products", sa.Column("valuation_method", sa.String(length=30), nullable=False, server_default="MOVING_AVERAGE"))

    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("supplier_type", sa.String(length=50), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_suppliers_tenant_code"),
    )
    op.create_index("ix_suppliers_tenant_id", "suppliers", ["tenant_id"], unique=False)
    op.create_index("ix_suppliers_code", "suppliers", ["code"], unique=False)

    op.create_table(
        "supplier_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_product_code", sa.String(length=100), nullable=True),
        sa.Column("minimum_order_qty", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_preferred", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["purchase_uom_id"], ["uoms.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "supplier_id", "product_id", name="uq_supplier_products_tenant_supplier_product"),
    )
    op.create_index("ix_supplier_products_tenant_id", "supplier_products", ["tenant_id"], unique=False)
    op.create_index("ix_supplier_products_supplier_id", "supplier_products", ["supplier_id"], unique=False)
    op.create_index("ix_supplier_products_product_id", "supplier_products", ["product_id"], unique=False)

    op.create_table(
        "supplier_price_histories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["supplier_product_id"], ["supplier_products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_supplier_price_histories_tenant_id", "supplier_price_histories", ["tenant_id"], unique=False)
    op.create_index("ix_supplier_price_histories_supplier_product_id", "supplier_price_histories", ["supplier_product_id"], unique=False)

    op.create_table(
        "purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("order_type", sa.String(length=20), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["purchase_request_id"], ["purchase_requests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "order_number", name="uq_purchase_orders_tenant_order_number"),
    )
    op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"], unique=False)
    op.create_index("ix_purchase_orders_sppg_id", "purchase_orders", ["sppg_id"], unique=False)
    op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"], unique=False)

    op.create_table(
        "purchase_order_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_request_line_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordered_quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("line_status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"]),
        sa.ForeignKeyConstraint(["purchase_request_line_id"], ["purchase_request_lines.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_purchase_order_lines_tenant_id", "purchase_order_lines", ["tenant_id"], unique=False)
    op.create_index("ix_purchase_order_lines_purchase_order_id", "purchase_order_lines", ["purchase_order_id"], unique=False)

    op.create_table(
        "stock_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location_type", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["stock_locations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "warehouse_id", "code", name="uq_stock_locations_tenant_warehouse_code"),
    )
    op.create_index("ix_stock_locations_tenant_id", "stock_locations", ["tenant_id"], unique=False)
    op.create_index("ix_stock_locations_warehouse_id", "stock_locations", ["warehouse_id"], unique=False)
    op.create_index("ix_stock_locations_sppg_id", "stock_locations", ["sppg_id"], unique=False)

    op.create_table(
        "inventory_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("batch_number", sa.String(length=100), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=True),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("quality_status", sa.String(length=30), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("quantity_on_hand", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("quantity_reserved", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("quantity_available", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["stock_locations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "product_id", "batch_number", name="uq_inventory_batches_tenant_product_batch"),
    )
    op.create_index("ix_inventory_batches_tenant_id", "inventory_batches", ["tenant_id"], unique=False)
    op.create_index("ix_inventory_batches_product_id", "inventory_batches", ["product_id"], unique=False)
    op.create_index("ix_inventory_batches_warehouse_id", "inventory_batches", ["warehouse_id"], unique=False)

    op.add_column("goods_receipts", sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_gr_po_id", "goods_receipts", "purchase_orders", ["purchase_order_id"], ["id"])
    op.create_index("ix_goods_receipts_purchase_order_id", "goods_receipts", ["purchase_order_id"], unique=False)

    op.add_column("goods_receipt_lines", sa.Column("purchase_order_line_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_grl_pol_id",
        "goods_receipt_lines",
        "purchase_order_lines",
        ["purchase_order_line_id"],
        ["id"],
    )

    op.add_column("inventory_transactions", sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("inventory_transactions", sa.Column("source_location_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("inventory_transactions", sa.Column("destination_location_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_inv_txn_batch", "inventory_transactions", "inventory_batches", ["batch_id"], ["id"])
    op.create_foreign_key("fk_inv_txn_src_loc", "inventory_transactions", "stock_locations", ["source_location_id"], ["id"])
    op.create_foreign_key("fk_inv_txn_dst_loc", "inventory_transactions", "stock_locations", ["destination_location_id"], ["id"])
    op.create_index("ix_inventory_transactions_batch_id", "inventory_transactions", ["batch_id"], unique=False)

    op.add_column("inventory_balances", sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_inv_bal_loc", "inventory_balances", "stock_locations", ["location_id"], ["id"])
    op.create_index("ix_inventory_balances_location_id", "inventory_balances", ["location_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_inventory_balances_location_id", table_name="inventory_balances")
    op.drop_constraint("fk_inv_bal_loc", "inventory_balances", type_="foreignkey")
    op.drop_column("inventory_balances", "location_id")

    op.drop_index("ix_inventory_transactions_batch_id", table_name="inventory_transactions")
    op.drop_constraint("fk_inv_txn_dst_loc", "inventory_transactions", type_="foreignkey")
    op.drop_constraint("fk_inv_txn_src_loc", "inventory_transactions", type_="foreignkey")
    op.drop_constraint("fk_inv_txn_batch", "inventory_transactions", type_="foreignkey")
    op.drop_column("inventory_transactions", "destination_location_id")
    op.drop_column("inventory_transactions", "source_location_id")
    op.drop_column("inventory_transactions", "batch_id")

    op.drop_constraint("fk_grl_pol_id", "goods_receipt_lines", type_="foreignkey")
    op.drop_column("goods_receipt_lines", "purchase_order_line_id")

    op.drop_index("ix_goods_receipts_purchase_order_id", table_name="goods_receipts")
    op.drop_constraint("fk_gr_po_id", "goods_receipts", type_="foreignkey")
    op.drop_column("goods_receipts", "purchase_order_id")

    op.drop_index("ix_inventory_batches_warehouse_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_product_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_tenant_id", table_name="inventory_batches")
    op.drop_table("inventory_batches")

    op.drop_index("ix_stock_locations_sppg_id", table_name="stock_locations")
    op.drop_index("ix_stock_locations_warehouse_id", table_name="stock_locations")
    op.drop_index("ix_stock_locations_tenant_id", table_name="stock_locations")
    op.drop_table("stock_locations")

    op.drop_index("ix_purchase_order_lines_purchase_order_id", table_name="purchase_order_lines")
    op.drop_index("ix_purchase_order_lines_tenant_id", table_name="purchase_order_lines")
    op.drop_table("purchase_order_lines")

    op.drop_index("ix_purchase_orders_supplier_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_sppg_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_tenant_id", table_name="purchase_orders")
    op.drop_table("purchase_orders")

    op.drop_index("ix_supplier_price_histories_supplier_product_id", table_name="supplier_price_histories")
    op.drop_index("ix_supplier_price_histories_tenant_id", table_name="supplier_price_histories")
    op.drop_table("supplier_price_histories")

    op.drop_index("ix_supplier_products_product_id", table_name="supplier_products")
    op.drop_index("ix_supplier_products_supplier_id", table_name="supplier_products")
    op.drop_index("ix_supplier_products_tenant_id", table_name="supplier_products")
    op.drop_table("supplier_products")

    op.drop_index("ix_suppliers_code", table_name="suppliers")
    op.drop_index("ix_suppliers_tenant_id", table_name="suppliers")
    op.drop_table("suppliers")

    op.drop_column("products", "valuation_method")
    op.drop_column("products", "reorder_point")
    op.drop_column("products", "maximum_stock")
    op.drop_column("products", "minimum_stock")
    op.drop_column("products", "track_expiry")
    op.drop_column("products", "track_batch")
