"""add uom product recipe meal plan"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_2045"
down_revision = "20260719_2005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uoms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("dimension", sa.String(length=30), nullable=False),
        sa.Column("factor_to_base", sa.Float(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_uoms_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_uoms")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_uoms_tenant_code"),
    )
    op.create_index(op.f("ix_uoms_code"), "uoms", ["code"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("stock_uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("standard_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["stock_uom_id"], ["uoms.id"], name=op.f("fk_products_stock_uom_id_uoms")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_products_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_products_tenant_code"),
    )
    op.create_index(op.f("ix_products_code"), "products", ["code"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("output_quantity", sa.Float(), nullable=False),
        sa.Column("output_uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["output_uom_id"], ["uoms.id"], name=op.f("fk_recipes_output_uom_id_uoms")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_recipes_product_id_products")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_recipes_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recipes")),
        sa.UniqueConstraint("tenant_id", "code", "version", name="uq_recipes_tenant_code_version"),
    )
    op.create_index(op.f("ix_recipes_code"), "recipes", ["code"], unique=False)

    op.create_table(
        "meal_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("planned_portions", sa.Integer(), nullable=False),
        sa.Column("budget_cost_per_portion", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], name=op.f("fk_meal_plans_recipe_id_recipes")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_meal_plans_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_meal_plans_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meal_plans")),
    )
    op.create_index("ix_meal_plans_tenant_id", "meal_plans", ["tenant_id"], unique=False)
    op.create_index("ix_meal_plans_sppg_id", "meal_plans", ["sppg_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_meal_plans_sppg_id", table_name="meal_plans")
    op.drop_index("ix_meal_plans_tenant_id", table_name="meal_plans")
    op.drop_table("meal_plans")
    op.drop_index(op.f("ix_recipes_code"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_products_code"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_uoms_code"), table_name="uoms")
    op.drop_table("uoms")
