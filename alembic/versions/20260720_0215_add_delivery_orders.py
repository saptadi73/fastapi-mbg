"""add delivery orders"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260720_0215"
down_revision = "20260720_0115"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "delivery_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_number", sa.String(length=100), nullable=False),
        sa.Column("planned_departure", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_arrival", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_portions", sa.Integer(), nullable=False),
        sa.Column("shipped_portions", sa.Integer(), nullable=True),
        sa.Column("received_portions", sa.Integer(), nullable=True),
        sa.Column("rejected_portions", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'PLANNED'")),
        sa.Column("receiver_name", sa.String(length=255), nullable=True),
        sa.Column("receiver_gps", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], name=op.f("fk_delivery_orders_production_order_id_production_orders")),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], name=op.f("fk_delivery_orders_school_id_schools")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_delivery_orders_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_delivery_orders_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_delivery_orders")),
        sa.UniqueConstraint("tenant_id", "delivery_number", name="uq_delivery_orders_tenant_delivery_number"),
    )
    op.create_index("ix_delivery_orders_delivery_number", "delivery_orders", ["delivery_number"], unique=False)
    op.create_index("ix_delivery_orders_production_order_id", "delivery_orders", ["production_order_id"], unique=False)
    op.create_index("ix_delivery_orders_school_id", "delivery_orders", ["school_id"], unique=False)
    op.create_index("ix_delivery_orders_sppg_id", "delivery_orders", ["sppg_id"], unique=False)
    op.create_index("ix_delivery_orders_tenant_id", "delivery_orders", ["tenant_id"], unique=False)

    op.create_table(
        "delivery_proofs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("receiver_name", sa.String(length=255), nullable=False),
        sa.Column("receiver_gps", sa.String(length=120), nullable=True),
        sa.Column("received_portions", sa.Integer(), nullable=False),
        sa.Column("rejected_portions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("temperature_celsius", sa.Float(), nullable=True),
        sa.Column("condition_notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["delivery_order_id"], ["delivery_orders.id"], name=op.f("fk_delivery_proofs_delivery_order_id_delivery_orders")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_delivery_proofs_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_delivery_proofs")),
    )
    op.create_index("ix_delivery_proofs_delivery_order_id", "delivery_proofs", ["delivery_order_id"], unique=False)
    op.create_index("ix_delivery_proofs_tenant_id", "delivery_proofs", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_delivery_proofs_tenant_id", table_name="delivery_proofs")
    op.drop_index("ix_delivery_proofs_delivery_order_id", table_name="delivery_proofs")
    op.drop_table("delivery_proofs")

    op.drop_index("ix_delivery_orders_tenant_id", table_name="delivery_orders")
    op.drop_index("ix_delivery_orders_sppg_id", table_name="delivery_orders")
    op.drop_index("ix_delivery_orders_school_id", table_name="delivery_orders")
    op.drop_index("ix_delivery_orders_production_order_id", table_name="delivery_orders")
    op.drop_index("ix_delivery_orders_delivery_number", table_name="delivery_orders")
    op.drop_table("delivery_orders")
