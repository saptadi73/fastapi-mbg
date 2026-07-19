"""add fleet foundation

Revision ID: 20260720_0705
Revises: 20260720_0655
Create Date: 2026-07-19 07:05:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0705"
down_revision: str | Sequence[str] | None = "20260720_0655"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicle_types",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("capacity_portions", sa.Integer(), nullable=True),
        sa.Column("capacity_kg", sa.Float(), nullable=True),
        sa.Column("temperature_controlled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_vehicle_types_tenant_code"),
    )
    op.create_index(op.f("ix_vehicle_types_code"), "vehicle_types", ["code"], unique=False)
    op.create_index(op.f("ix_vehicle_types_tenant_id"), "vehicle_types", ["tenant_id"], unique=False)

    op.create_table(
        "drivers",
        sa.Column("driver_code", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("license_number", sa.String(length=100), nullable=False),
        sa.Column("license_type", sa.String(length=50), nullable=True),
        sa.Column("license_expiry_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "driver_code", name="uq_drivers_tenant_driver_code"),
        sa.UniqueConstraint("tenant_id", "license_number", name="uq_drivers_tenant_license_number"),
    )
    op.create_index(op.f("ix_drivers_driver_code"), "drivers", ["driver_code"], unique=False)
    op.create_index(op.f("ix_drivers_license_number"), "drivers", ["license_number"], unique=False)
    op.create_index(op.f("ix_drivers_status"), "drivers", ["status"], unique=False)
    op.create_index(op.f("ix_drivers_tenant_id"), "drivers", ["tenant_id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("home_sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_code", sa.String(length=100), nullable=False),
        sa.Column("plate_number", sa.String(length=100), nullable=False),
        sa.Column("ownership_status", sa.String(length=50), nullable=False, server_default="OWNED"),
        sa.Column("brand_name", sa.String(length=100), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("manufacture_year", sa.Integer(), nullable=True),
        sa.Column("capacity_portions", sa.Integer(), nullable=True),
        sa.Column("fuel_type", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["home_sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vehicle_type_id"], ["vehicle_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "plate_number", name="uq_vehicles_tenant_plate_number"),
        sa.UniqueConstraint("tenant_id", "vehicle_code", name="uq_vehicles_tenant_vehicle_code"),
    )
    op.create_index(op.f("ix_vehicles_home_sppg_id"), "vehicles", ["home_sppg_id"], unique=False)
    op.create_index(op.f("ix_vehicles_plate_number"), "vehicles", ["plate_number"], unique=False)
    op.create_index(op.f("ix_vehicles_status"), "vehicles", ["status"], unique=False)
    op.create_index(op.f("ix_vehicles_tenant_id"), "vehicles", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vehicles_vehicle_code"), "vehicles", ["vehicle_code"], unique=False)
    op.create_index(op.f("ix_vehicles_vehicle_type_id"), "vehicles", ["vehicle_type_id"], unique=False)

    op.create_table(
        "vehicle_assignments",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assignment_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("assignment_role", sa.String(length=50), nullable=False, server_default="DELIVERY"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ASSIGNED"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicle_assignments_assignment_date"), "vehicle_assignments", ["assignment_date"], unique=False)
    op.create_index(op.f("ix_vehicle_assignments_driver_id"), "vehicle_assignments", ["driver_id"], unique=False)
    op.create_index(op.f("ix_vehicle_assignments_sppg_id"), "vehicle_assignments", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_vehicle_assignments_status"), "vehicle_assignments", ["status"], unique=False)
    op.create_index(op.f("ix_vehicle_assignments_tenant_id"), "vehicle_assignments", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vehicle_assignments_vehicle_id"), "vehicle_assignments", ["vehicle_id"], unique=False)

    op.create_table(
        "vehicle_maintenances",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("maintenance_date", sa.Date(), nullable=False),
        sa.Column("maintenance_type", sa.String(length=100), nullable=False),
        sa.Column("odometer_km", sa.Float(), nullable=True),
        sa.Column("cost_amount", sa.Float(), nullable=True),
        sa.Column("vendor_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="COMPLETED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicle_maintenances_maintenance_date"), "vehicle_maintenances", ["maintenance_date"], unique=False)
    op.create_index(op.f("ix_vehicle_maintenances_maintenance_type"), "vehicle_maintenances", ["maintenance_type"], unique=False)
    op.create_index(op.f("ix_vehicle_maintenances_sppg_id"), "vehicle_maintenances", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_vehicle_maintenances_status"), "vehicle_maintenances", ["status"], unique=False)
    op.create_index(op.f("ix_vehicle_maintenances_tenant_id"), "vehicle_maintenances", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vehicle_maintenances_vehicle_id"), "vehicle_maintenances", ["vehicle_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_vehicle_maintenances_vehicle_id"), table_name="vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_maintenances_tenant_id"), table_name="vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_maintenances_status"), table_name="vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_maintenances_sppg_id"), table_name="vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_maintenances_maintenance_type"), table_name="vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_maintenances_maintenance_date"), table_name="vehicle_maintenances")
    op.drop_table("vehicle_maintenances")
    op.drop_index(op.f("ix_vehicle_assignments_vehicle_id"), table_name="vehicle_assignments")
    op.drop_index(op.f("ix_vehicle_assignments_tenant_id"), table_name="vehicle_assignments")
    op.drop_index(op.f("ix_vehicle_assignments_status"), table_name="vehicle_assignments")
    op.drop_index(op.f("ix_vehicle_assignments_sppg_id"), table_name="vehicle_assignments")
    op.drop_index(op.f("ix_vehicle_assignments_driver_id"), table_name="vehicle_assignments")
    op.drop_index(op.f("ix_vehicle_assignments_assignment_date"), table_name="vehicle_assignments")
    op.drop_table("vehicle_assignments")
    op.drop_index(op.f("ix_vehicles_vehicle_type_id"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_vehicle_code"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_tenant_id"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_status"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_plate_number"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_home_sppg_id"), table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index(op.f("ix_drivers_tenant_id"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_status"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_license_number"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_driver_code"), table_name="drivers")
    op.drop_table("drivers")
    op.drop_index(op.f("ix_vehicle_types_tenant_id"), table_name="vehicle_types")
    op.drop_index(op.f("ix_vehicle_types_code"), table_name="vehicle_types")
    op.drop_table("vehicle_types")
