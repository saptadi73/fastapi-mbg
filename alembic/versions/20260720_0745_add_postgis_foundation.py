"""add postgis foundation

Revision ID: 20260720_0745
Revises: 20260720_0735
Create Date: 2026-07-20 07:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geography, Geometry
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0745"
down_revision: str | Sequence[str] | None = "20260720_0735"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.add_column("sppg", sa.Column("location", Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True))
    op.add_column("schools", sa.Column("location", Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True))

    op.execute(
        """
        UPDATE sppg
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
        WHERE location IS NULL
        """
    )
    op.execute(
        """
        UPDATE schools
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
        WHERE location IS NULL
        """
    )

    op.alter_column("sppg", "location", nullable=False)
    op.alter_column("schools", "location", nullable=False)

    op.execute("CREATE INDEX IF NOT EXISTS ix_sppg_location_gist ON sppg USING GIST (location)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_schools_location_gist ON schools USING GIST (location)")

    op.create_table(
        "service_areas",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("boundary", Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_areas_sppg_id"), "service_areas", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_service_areas_tenant_id"), "service_areas", ["tenant_id"], unique=False)
    op.execute("CREATE INDEX IF NOT EXISTS ix_service_areas_boundary_gist ON service_areas USING GIST (boundary)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_service_areas_boundary_gist")
    op.drop_index(op.f("ix_service_areas_tenant_id"), table_name="service_areas")
    op.drop_index(op.f("ix_service_areas_sppg_id"), table_name="service_areas")
    op.drop_table("service_areas")
    op.execute("DROP INDEX IF EXISTS ix_schools_location_gist")
    op.execute("DROP INDEX IF EXISTS ix_sppg_location_gist")
    op.drop_column("schools", "location")
    op.drop_column("sppg", "location")
