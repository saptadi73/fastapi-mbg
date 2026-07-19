"""add recipe lines"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_2115"
down_revision = "20260719_2045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("component_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("waste_percentage", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["component_product_id"], ["products.id"], name=op.f("fk_recipe_lines_component_product_id_products")),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], name=op.f("fk_recipe_lines_recipe_id_recipes")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_recipe_lines_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_recipe_lines_uom_id_uoms")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recipe_lines")),
    )
    op.create_index("ix_recipe_lines_recipe_id", "recipe_lines", ["recipe_id"], unique=False)
    op.create_index("ix_recipe_lines_tenant_id", "recipe_lines", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_lines_tenant_id", table_name="recipe_lines")
    op.drop_index("ix_recipe_lines_recipe_id", table_name="recipe_lines")
    op.drop_table("recipe_lines")
