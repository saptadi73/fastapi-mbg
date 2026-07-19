"""add inventory foundation"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_2230"
down_revision = "20260719_2115"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "warehouses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("warehouse_type", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_warehouses_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_warehouses_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_warehouses")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_warehouses_tenant_code"),
    )
    op.create_index("ix_warehouses_code", "warehouses", ["code"], unique=False)
    op.create_index("ix_warehouses_sppg_id", "warehouses", ["sppg_id"], unique=False)
    op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"], unique=False)

    op.create_table(
        "inventory_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_warehouse_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("destination_warehouse_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("transaction_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(
            ["destination_warehouse_id"],
            ["warehouses.id"],
            name=op.f("fk_inventory_transactions_destination_warehouse_id_warehouses"),
        ),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], name=op.f("fk_inventory_transactions_posted_by_users")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_inventory_transactions_product_id_products")),
        sa.ForeignKeyConstraint(
            ["source_warehouse_id"],
            ["warehouses.id"],
            name=op.f("fk_inventory_transactions_source_warehouse_id_warehouses"),
        ),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_inventory_transactions_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_inventory_transactions_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_inventory_transactions_uom_id_uoms")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_transactions")),
    )
    op.create_index("ix_inventory_transactions_product_id", "inventory_transactions", ["product_id"], unique=False)
    op.create_index("ix_inventory_transactions_sppg_id", "inventory_transactions", ["sppg_id"], unique=False)
    op.create_index("ix_inventory_transactions_tenant_id", "inventory_transactions", ["tenant_id"], unique=False)
    op.create_index("ix_inventory_transactions_transaction_type", "inventory_transactions", ["transaction_type"], unique=False)

    op.create_table(
        "inventory_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_on_hand", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("quantity_reserved", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("quantity_available", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("average_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_inventory_balances_product_id_products")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_inventory_balances_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_inventory_balances_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], name=op.f("fk_inventory_balances_warehouse_id_warehouses")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_balances")),
        sa.UniqueConstraint("tenant_id", "warehouse_id", "product_id", name="uq_inventory_balances_tenant_wh_product"),
    )
    op.create_index("ix_inventory_balances_product_id", "inventory_balances", ["product_id"], unique=False)
    op.create_index("ix_inventory_balances_sppg_id", "inventory_balances", ["sppg_id"], unique=False)
    op.create_index("ix_inventory_balances_tenant_id", "inventory_balances", ["tenant_id"], unique=False)
    op.create_index("ix_inventory_balances_warehouse_id", "inventory_balances", ["warehouse_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_inventory_balances_warehouse_id", table_name="inventory_balances")
    op.drop_index("ix_inventory_balances_tenant_id", table_name="inventory_balances")
    op.drop_index("ix_inventory_balances_sppg_id", table_name="inventory_balances")
    op.drop_index("ix_inventory_balances_product_id", table_name="inventory_balances")
    op.drop_table("inventory_balances")

    op.drop_index("ix_inventory_transactions_transaction_type", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_tenant_id", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_sppg_id", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_product_id", table_name="inventory_transactions")
    op.drop_table("inventory_transactions")

    op.drop_index("ix_warehouses_tenant_id", table_name="warehouses")
    op.drop_index("ix_warehouses_sppg_id", table_name="warehouses")
    op.drop_index("ix_warehouses_code", table_name="warehouses")
    op.drop_table("warehouses")
