"""add active sppg id to users

Revision ID: 20260720_0455
Revises: 20260720_0445
Create Date: 2026-07-20 04:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0455"
down_revision: str | None = "20260720_0445"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("active_sppg_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        op.f("fk_users_active_sppg_id_sppg"),
        "users",
        "sppg",
        ["active_sppg_id"],
        ["id"],
    )
    op.create_index(op.f("ix_users_active_sppg_id"), "users", ["active_sppg_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_active_sppg_id"), table_name="users")
    op.drop_constraint(op.f("fk_users_active_sppg_id_sppg"), "users", type_="foreignkey")
    op.drop_column("users", "active_sppg_id")
