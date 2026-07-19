"""add workforce foundation

Revision ID: 20260720_0645
Revises: 20260720_0635
Create Date: 2026-07-19 06:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0645"
down_revision: str | Sequence[str] | None = "20260720_0635"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "positions",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_positions_tenant_code"),
    )
    op.create_index(op.f("ix_positions_code"), "positions", ["code"], unique=False)
    op.create_index(op.f("ix_positions_tenant_id"), "positions", ["tenant_id"], unique=False)

    op.create_table(
        "employees",
        sa.Column("position_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("employee_code", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("employment_type", sa.String(length=50), nullable=False, server_default="PERMANENT"),
        sa.Column("join_date", sa.Date(), nullable=False),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("daily_rate", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["position_id"], ["positions.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "employee_code", name="uq_employees_tenant_employee_code"),
    )
    op.create_index(op.f("ix_employees_employee_code"), "employees", ["employee_code"], unique=False)
    op.create_index(op.f("ix_employees_position_id"), "employees", ["position_id"], unique=False)
    op.create_index(op.f("ix_employees_tenant_id"), "employees", ["tenant_id"], unique=False)

    op.create_table(
        "employee_assignments",
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("assignment_role", sa.String(length=100), nullable=False, server_default="OPERATOR"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_assignments_employee_id"), "employee_assignments", ["employee_id"], unique=False)
    op.create_index(op.f("ix_employee_assignments_sppg_id"), "employee_assignments", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_employee_assignments_tenant_id"), "employee_assignments", ["tenant_id"], unique=False)

    op.create_table(
        "work_shifts",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("shift_date", sa.Date(), nullable=False),
        sa.Column("shift_name", sa.String(length=100), nullable=False),
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PLANNED"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["employee_assignments.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_work_shifts_assignment_id"), "work_shifts", ["assignment_id"], unique=False)
    op.create_index(op.f("ix_work_shifts_employee_id"), "work_shifts", ["employee_id"], unique=False)
    op.create_index(op.f("ix_work_shifts_sppg_id"), "work_shifts", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_work_shifts_tenant_id"), "work_shifts", ["tenant_id"], unique=False)

    op.create_table(
        "attendances",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shift_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("check_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attendance_status", sa.String(length=50), nullable=False, server_default="PRESENT"),
        sa.Column("worked_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["shift_id"], ["work_shifts.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendances_employee_id"), "attendances", ["employee_id"], unique=False)
    op.create_index(op.f("ix_attendances_shift_id"), "attendances", ["shift_id"], unique=False)
    op.create_index(op.f("ix_attendances_sppg_id"), "attendances", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_attendances_tenant_id"), "attendances", ["tenant_id"], unique=False)

    op.create_table(
        "timesheets",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timesheets_employee_id"), "timesheets", ["employee_id"], unique=False)
    op.create_index(op.f("ix_timesheets_sppg_id"), "timesheets", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_timesheets_tenant_id"), "timesheets", ["tenant_id"], unique=False)

    op.create_table(
        "labor_costs",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timesheet_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cost_date", sa.Date(), nullable=False),
        sa.Column("cost_component", sa.String(length=100), nullable=False, server_default="LABOR"),
        sa.Column("hours_worked", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hourly_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["timesheet_id"], ["timesheets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_labor_costs_employee_id"), "labor_costs", ["employee_id"], unique=False)
    op.create_index(op.f("ix_labor_costs_sppg_id"), "labor_costs", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_labor_costs_tenant_id"), "labor_costs", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_labor_costs_timesheet_id"), "labor_costs", ["timesheet_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_labor_costs_timesheet_id"), table_name="labor_costs")
    op.drop_index(op.f("ix_labor_costs_tenant_id"), table_name="labor_costs")
    op.drop_index(op.f("ix_labor_costs_sppg_id"), table_name="labor_costs")
    op.drop_index(op.f("ix_labor_costs_employee_id"), table_name="labor_costs")
    op.drop_table("labor_costs")
    op.drop_index(op.f("ix_timesheets_tenant_id"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_sppg_id"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_employee_id"), table_name="timesheets")
    op.drop_table("timesheets")
    op.drop_index(op.f("ix_attendances_tenant_id"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_sppg_id"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_shift_id"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_employee_id"), table_name="attendances")
    op.drop_table("attendances")
    op.drop_index(op.f("ix_work_shifts_tenant_id"), table_name="work_shifts")
    op.drop_index(op.f("ix_work_shifts_sppg_id"), table_name="work_shifts")
    op.drop_index(op.f("ix_work_shifts_employee_id"), table_name="work_shifts")
    op.drop_index(op.f("ix_work_shifts_assignment_id"), table_name="work_shifts")
    op.drop_table("work_shifts")
    op.drop_index(op.f("ix_employee_assignments_tenant_id"), table_name="employee_assignments")
    op.drop_index(op.f("ix_employee_assignments_sppg_id"), table_name="employee_assignments")
    op.drop_index(op.f("ix_employee_assignments_employee_id"), table_name="employee_assignments")
    op.drop_table("employee_assignments")
    op.drop_index(op.f("ix_employees_tenant_id"), table_name="employees")
    op.drop_index(op.f("ix_employees_position_id"), table_name="employees")
    op.drop_index(op.f("ix_employees_employee_code"), table_name="employees")
    op.drop_table("employees")
    op.drop_index(op.f("ix_positions_tenant_id"), table_name="positions")
    op.drop_index(op.f("ix_positions_code"), table_name="positions")
    op.drop_table("positions")
