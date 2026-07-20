"""add vehicle location tracking

Revision ID: 20260720_1205
Revises: 20260720_1135
Create Date: 2026-07-20 12:05:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "20260720_1205"
down_revision: str | Sequence[str] | None = "20260720_1135"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicle_locations",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("location", Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False),
        sa.Column("speed_kph", sa.Float(), nullable=True),
        sa.Column("heading_degree", sa.Float(), nullable=True),
        sa.Column("accuracy_meter", sa.Float(), nullable=True),
        sa.Column("engine_on", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("movement_status", sa.String(length=50), nullable=False, server_default="IDLE"),
        sa.Column("event_type", sa.String(length=50), nullable=False, server_default="PING"),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("address_label", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["vehicle_assignments.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicle_locations_assignment_id"), "vehicle_locations", ["assignment_id"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_event_type"), "vehicle_locations", ["event_type"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_movement_status"), "vehicle_locations", ["movement_status"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_recorded_at"), "vehicle_locations", ["recorded_at"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_sppg_id"), "vehicle_locations", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_tenant_id"), "vehicle_locations", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vehicle_locations_vehicle_id"), "vehicle_locations", ["vehicle_id"], unique=False)
    op.execute("CREATE INDEX IF NOT EXISTS ix_vehicle_locations_location_gist ON vehicle_locations USING GIST (location)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_vehicle_locations_location_gist")
    op.drop_index(op.f("ix_vehicle_locations_vehicle_id"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_tenant_id"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_sppg_id"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_recorded_at"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_movement_status"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_event_type"), table_name="vehicle_locations")
    op.drop_index(op.f("ix_vehicle_locations_assignment_id"), table_name="vehicle_locations")
    op.drop_table("vehicle_locations")
