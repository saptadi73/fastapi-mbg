"""add user sppg access

Revision ID: 20260720_0505
Revises: 20260720_0455
Create Date: 2026-07-20 05:05:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0505"
down_revision: str | None = "20260720_0455"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_sppg_access",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_user_sppg_access_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_user_sppg_access_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_sppg_access_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_sppg_access")),
        sa.UniqueConstraint("user_id", "sppg_id", name="uq_user_sppg_access_user_sppg"),
    )
    op.create_index(op.f("ix_user_sppg_access_user_id"), "user_sppg_access", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_sppg_access_tenant_id"), "user_sppg_access", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_user_sppg_access_sppg_id"), "user_sppg_access", ["sppg_id"], unique=False)
    op.execute(
        """
        INSERT INTO user_sppg_access (user_id, tenant_id, sppg_id)
        SELECT id, tenant_id, active_sppg_id
        FROM users
        WHERE active_sppg_id IS NOT NULL
        ON CONFLICT (user_id, sppg_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_sppg_access_sppg_id"), table_name="user_sppg_access")
    op.drop_index(op.f("ix_user_sppg_access_tenant_id"), table_name="user_sppg_access")
    op.drop_index(op.f("ix_user_sppg_access_user_id"), table_name="user_sppg_access")
    op.drop_table("user_sppg_access")
