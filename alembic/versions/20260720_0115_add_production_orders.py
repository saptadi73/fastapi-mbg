"""add production orders"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260720_0115"
down_revision = "20260720_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "production_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meal_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("production_number", sa.String(length=100), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'PLANNED'")),
        sa.Column("planned_portions", sa.Integer(), nullable=False),
        sa.Column("actual_portions", sa.Integer(), nullable=True),
        sa.Column("accepted_portions", sa.Integer(), nullable=True),
        sa.Column("rejected_portions", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_total_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("actual_cost_per_portion", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"], name=op.f("fk_production_orders_meal_plan_id_meal_plans")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_production_orders_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_production_orders_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_production_orders")),
        sa.UniqueConstraint("tenant_id", "production_number", name="uq_production_orders_tenant_production_number"),
    )
    op.create_index("ix_production_orders_meal_plan_id", "production_orders", ["meal_plan_id"], unique=False)
    op.create_index("ix_production_orders_production_number", "production_orders", ["production_number"], unique=False)
    op.create_index("ix_production_orders_sppg_id", "production_orders", ["sppg_id"], unique=False)
    op.create_index("ix_production_orders_tenant_id", "production_orders", ["tenant_id"], unique=False)

    op.create_table(
        "production_material_consumptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("planned_quantity", sa.Float(), nullable=False),
        sa.Column("actual_quantity", sa.Float(), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_production_material_consumptions_product_id_products")),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], name=op.f("fk_production_material_consumptions_production_order_id_production_orders")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_production_material_consumptions_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_production_material_consumptions_uom_id_uoms")),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], name=op.f("fk_production_material_consumptions_warehouse_id_warehouses")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_production_material_consumptions")),
    )
    op.create_index("ix_production_material_consumptions_product_id", "production_material_consumptions", ["product_id"], unique=False)
    op.create_index("ix_production_material_consumptions_production_order_id", "production_material_consumptions", ["production_order_id"], unique=False)
    op.create_index("ix_production_material_consumptions_tenant_id", "production_material_consumptions", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_production_material_consumptions_tenant_id", table_name="production_material_consumptions")
    op.drop_index("ix_production_material_consumptions_production_order_id", table_name="production_material_consumptions")
    op.drop_index("ix_production_material_consumptions_product_id", table_name="production_material_consumptions")
    op.drop_table("production_material_consumptions")

    op.drop_index("ix_production_orders_tenant_id", table_name="production_orders")
    op.drop_index("ix_production_orders_sppg_id", table_name="production_orders")
    op.drop_index("ix_production_orders_production_number", table_name="production_orders")
    op.drop_index("ix_production_orders_meal_plan_id", table_name="production_orders")
    op.drop_table("production_orders")
