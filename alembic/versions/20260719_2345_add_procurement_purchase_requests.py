"""add procurement purchase requests"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_2345"
down_revision = "20260719_2230"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meal_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_number", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"], name=op.f("fk_purchase_requests_meal_plan_id_meal_plans")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_purchase_requests_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_purchase_requests_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_purchase_requests")),
        sa.UniqueConstraint("tenant_id", "request_number", name="uq_purchase_requests_tenant_request_number"),
    )
    op.create_index("ix_purchase_requests_request_number", "purchase_requests", ["request_number"], unique=False)
    op.create_index("ix_purchase_requests_sppg_id", "purchase_requests", ["sppg_id"], unique=False)
    op.create_index("ix_purchase_requests_tenant_id", "purchase_requests", ["tenant_id"], unique=False)

    op.create_table(
        "purchase_request_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_quantity", sa.Float(), nullable=False),
        sa.Column("shortage_quantity", sa.Float(), nullable=False),
        sa.Column("estimated_unit_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("estimated_total_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_purchase_request_lines_product_id_products")),
        sa.ForeignKeyConstraint(["purchase_request_id"], ["purchase_requests.id"], name=op.f("fk_purchase_request_lines_purchase_request_id_purchase_requests")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_purchase_request_lines_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["uom_id"], ["uoms.id"], name=op.f("fk_purchase_request_lines_uom_id_uoms")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_purchase_request_lines")),
    )
    op.create_index("ix_purchase_request_lines_product_id", "purchase_request_lines", ["product_id"], unique=False)
    op.create_index("ix_purchase_request_lines_purchase_request_id", "purchase_request_lines", ["purchase_request_id"], unique=False)
    op.create_index("ix_purchase_request_lines_tenant_id", "purchase_request_lines", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_purchase_request_lines_tenant_id", table_name="purchase_request_lines")
    op.drop_index("ix_purchase_request_lines_purchase_request_id", table_name="purchase_request_lines")
    op.drop_index("ix_purchase_request_lines_product_id", table_name="purchase_request_lines")
    op.drop_table("purchase_request_lines")

    op.drop_index("ix_purchase_requests_tenant_id", table_name="purchase_requests")
    op.drop_index("ix_purchase_requests_sppg_id", table_name="purchase_requests")
    op.drop_index("ix_purchase_requests_request_number", table_name="purchase_requests")
    op.drop_table("purchase_requests")
