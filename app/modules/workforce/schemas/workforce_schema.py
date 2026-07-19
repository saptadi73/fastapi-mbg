from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PositionCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


class EmployeeCreate(BaseModel):
    tenant_id: str
    position_id: str | None = None
    employee_code: str
    full_name: str
    employment_type: str = "PERMANENT"
    join_date: date
    phone_number: str | None = None
    daily_rate: float | None = None
    is_active: bool = True


class EmployeeAssignmentCreate(BaseModel):
    sppg_id: str
    start_date: date
    end_date: date | None = None
    assignment_role: str = "OPERATOR"
    is_primary: bool = True
    is_active: bool = True
    notes: str | None = None


class WorkShiftCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    employee_id: str
    assignment_id: str | None = None
    shift_date: date
    shift_name: str
    planned_start_at: datetime
    planned_end_at: datetime
    status: str = "PLANNED"
    notes: str | None = None


class AttendanceCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    employee_id: str
    shift_id: str | None = None
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    attendance_status: str = "PRESENT"
    notes: str | None = None


class TimesheetCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    employee_id: str
    period_start: date
    period_end: date
    total_days: int
    total_hours: float
    status: str = "DRAFT"
    notes: str | None = None


class LaborCostCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    employee_id: str
    timesheet_id: str | None = None
    cost_date: date
    cost_component: str = "LABOR"
    hours_worked: float
    hourly_rate: float
    notes: str | None = None


class PositionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    position_id: UUID | None
    employee_code: str
    full_name: str
    employment_type: str
    join_date: date
    phone_number: str | None
    daily_rate: float | None
    is_active: bool


class EmployeeAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    employee_id: UUID
    sppg_id: UUID
    start_date: date
    end_date: date | None
    assignment_role: str
    is_primary: bool
    is_active: bool
    notes: str | None


class WorkShiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    employee_id: UUID
    assignment_id: UUID | None
    shift_date: date
    shift_name: str
    planned_start_at: datetime
    planned_end_at: datetime
    status: str
    notes: str | None


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    employee_id: UUID
    shift_id: UUID | None
    check_in_at: datetime | None
    check_out_at: datetime | None
    attendance_status: str
    worked_hours: float
    notes: str | None


class TimesheetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    employee_id: UUID
    period_start: date
    period_end: date
    total_days: int
    total_hours: float
    status: str
    notes: str | None


class LaborCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    employee_id: UUID
    timesheet_id: UUID | None
    cost_date: date
    cost_component: str
    hours_worked: float
    hourly_rate: float
    total_cost: float
    notes: str | None


class EmployeeBundleRead(BaseModel):
    employee: EmployeeRead
    assignments: list[EmployeeAssignmentRead]
