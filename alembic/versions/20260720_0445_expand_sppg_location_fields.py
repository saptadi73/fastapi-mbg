"""expand sppg location fields

Revision ID: 20260720_0445
Revises: 20260720_0430
Create Date: 2026-07-20 04:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0445"
down_revision: str | None = "20260720_0430"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("sppg", sa.Column("address", sa.String(length=500), nullable=True))
    op.add_column("sppg", sa.Column("province", sa.String(length=120), nullable=True))
    op.add_column("sppg", sa.Column("district", sa.String(length=120), nullable=True))
    op.add_column("sppg", sa.Column("village", sa.String(length=120), nullable=True))
    op.add_column(
        "sppg",
        sa.Column("service_radius_meter", sa.Float(), nullable=False, server_default=sa.text("3000")),
    )
    op.add_column(
        "sppg",
        sa.Column("timezone", sa.String(length=60), nullable=False, server_default=sa.text("'Asia/Jakarta'")),
    )
    op.add_column(
        "sppg",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.execute("UPDATE sppg SET address = city WHERE address IS NULL")
    op.alter_column("sppg", "address", nullable=False)

    op.alter_column("sppg", "service_radius_meter", server_default=None)
    op.alter_column("sppg", "timezone", server_default=None)
    op.alter_column("sppg", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_column("sppg", "is_active")
    op.drop_column("sppg", "timezone")
    op.drop_column("sppg", "service_radius_meter")
    op.drop_column("sppg", "village")
    op.drop_column("sppg", "district")
    op.drop_column("sppg", "province")
    op.drop_column("sppg", "address")
