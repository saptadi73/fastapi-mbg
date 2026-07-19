"""align postgis geometry model

Revision ID: 20260720_0815
Revises: 20260720_0745
Create Date: 2026-07-20 08:15:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260720_0815"
down_revision: str | Sequence[str] | None = "20260720_0745"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_sppg_location_gist")
    op.execute("DROP INDEX IF EXISTS ix_schools_location_gist")
    op.execute("DROP INDEX IF EXISTS ix_service_areas_boundary_gist")

    op.execute(
        """
        ALTER TABLE sppg
        ALTER COLUMN location TYPE geometry(POINT, 4326)
        USING ST_SetSRID(location::geometry, 4326)
        """
    )
    op.execute(
        """
        ALTER TABLE schools
        ALTER COLUMN location TYPE geometry(POINT, 4326)
        USING ST_SetSRID(location::geometry, 4326)
        """
    )
    op.execute(
        """
        ALTER TABLE service_areas
        ALTER COLUMN boundary TYPE geometry(MULTIPOLYGON, 4326)
        USING ST_Multi(ST_SetSRID(boundary::geometry, 4326))
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_sppg_location_gist ON sppg USING GIST (location)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_schools_location_gist ON schools USING GIST (location)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_service_areas_boundary_gist ON service_areas USING GIST (boundary)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_service_areas_boundary_gist")
    op.execute("DROP INDEX IF EXISTS ix_schools_location_gist")
    op.execute("DROP INDEX IF EXISTS ix_sppg_location_gist")

    op.execute(
        """
        ALTER TABLE service_areas
        ALTER COLUMN boundary TYPE geometry(POLYGON, 4326)
        USING ST_GeometryN(ST_SetSRID(boundary::geometry, 4326), 1)
        """
    )
    op.execute(
        """
        ALTER TABLE schools
        ALTER COLUMN location TYPE geography(POINT, 4326)
        USING ST_SetSRID(location::geometry, 4326)::geography
        """
    )
    op.execute(
        """
        ALTER TABLE sppg
        ALTER COLUMN location TYPE geography(POINT, 4326)
        USING ST_SetSRID(location::geometry, 4326)::geography
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_sppg_location_gist ON sppg USING GIST (location)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_schools_location_gist ON schools USING GIST (location)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_service_areas_boundary_gist ON service_areas USING GIST (boundary)")
