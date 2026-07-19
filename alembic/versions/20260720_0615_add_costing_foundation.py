"""add costing foundation

Revision ID: 20260720_0615
Revises: 20260720_0605
Create Date: 2026-07-20 06:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0615"
down_revision: str | None = "20260720_0605"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cost_policies",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("labor_cost_per_portion", sa.Float(), nullable=False, server_default="0"),
        sa.Column("utility_cost_per_portion", sa.Float(), nullable=False, server_default="0"),
        sa.Column("packaging_cost_per_portion", sa.Float(), nullable=False, server_default="0"),
        sa.Column("distribution_cost_per_portion", sa.Float(), nullable=False, server_default="0"),
        sa.Column("overhead_cost_per_portion", sa.Float(), nullable=False, server_default="0"),
        sa.Column("waste_cost_percentage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_cost_policies_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_cost_policies_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cost_policies")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_cost_policies_tenant_code"),
    )
    op.create_index(op.f("ix_cost_policies_tenant_id"), "cost_policies", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_cost_policies_sppg_id"), "cost_policies", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_cost_policies_code"), "cost_policies", ["code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cost_policies_code"), table_name="cost_policies")
    op.drop_index(op.f("ix_cost_policies_sppg_id"), table_name="cost_policies")
    op.drop_index(op.f("ix_cost_policies_tenant_id"), table_name="cost_policies")
    op.drop_table("cost_policies")
