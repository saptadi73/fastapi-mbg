from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workforce.models.attendance import Attendance
from app.modules.workforce.models.employee import Employee
from app.modules.workforce.models.employee_assignment import EmployeeAssignment
from app.modules.workforce.models.labor_cost import LaborCost
from app.modules.workforce.models.position import Position
from app.modules.workforce.models.timesheet import Timesheet
from app.modules.workforce.models.work_shift import WorkShift
from app.modules.workforce.repositories.workforce_repository import WorkforceRepository
from app.modules.workforce.schemas.workforce_schema import (
    AttendanceCreate,
    EmployeeAssignmentCreate,
    EmployeeCreate,
    LaborCostCreate,
    PositionCreate,
    TimesheetCreate,
    WorkShiftCreate,
)
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class WorkforceService:
    def __init__(
        self,
        repository: WorkforceRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def list_positions(self) -> list[Position]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_positions(tenant_id=tenant_id)

    async def create_position(self, payload: PositionCreate) -> Position:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant workforce tidak ditemukan.")
        if await self.repository.get_position_by_tenant_code(tenant_id, payload.code) is not None:
            raise ConflictException(code="POSITION_CODE_ALREADY_EXISTS", message="Kode posisi sudah digunakan.")
        return await self.repository.add_position(
            Position(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                description=payload.description,
                is_active=payload.is_active,
            )
        )

    async def list_employees(self) -> list[Employee]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_employees(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_employee_bundle(self, employee_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        employee = await self.repository.get_employee_by_id_and_scope(employee_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if employee is None:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee tidak ditemukan.")
        return {"employee": employee, "assignments": await self.repository.list_assignments(employee.id)}

    async def create_employee(self, payload: EmployeeCreate) -> Employee:
        tenant_id = UUID(payload.tenant_id)
        position_id = UUID(payload.position_id) if payload.position_id else None
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant employee tidak ditemukan.")
        if await self.repository.get_employee_by_tenant_code(tenant_id, payload.employee_code) is not None:
            raise ConflictException(code="EMPLOYEE_CODE_ALREADY_EXISTS", message="Kode employee sudah digunakan.")
        if position_id is not None:
            position = await self.repository.get_position_by_id(position_id)
            if position is None or position.tenant_id != tenant_id:
                raise NotFoundException(code="POSITION_NOT_FOUND", message="Position employee tidak ditemukan.")
        return await self.repository.add_employee(
            Employee(
                tenant_id=tenant_id,
                position_id=position_id,
                employee_code=payload.employee_code,
                full_name=payload.full_name,
                employment_type=payload.employment_type,
                join_date=payload.join_date,
                phone_number=payload.phone_number,
                daily_rate=payload.daily_rate,
                is_active=payload.is_active,
            )
        )

    async def assign_employee(self, employee_id: UUID, payload: EmployeeAssignmentCreate) -> EmployeeAssignment:
        employee = await self.repository.get_employee_by_id(employee_id)
        if employee is None:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee tidak ditemukan.")
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(employee.tenant_id)
        enforce_sppg_write_scope(sppg_id)
        if payload.end_date and payload.end_date < payload.start_date:
            raise BadRequestException(code="INVALID_ASSIGNMENT_DATE_RANGE", message="Tanggal assignment employee tidak valid.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != employee.tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG assignment employee tidak ditemukan.")
        if await self.repository.get_assignment_by_employee_and_sppg(employee_id, sppg_id) is not None:
            raise ConflictException(code="EMPLOYEE_ALREADY_ASSIGNED", message="Employee sudah aktif di SPPG ini.")
        return await self.repository.add_assignment(
            EmployeeAssignment(
                tenant_id=employee.tenant_id,
                employee_id=employee.id,
                sppg_id=sppg_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                assignment_role=payload.assignment_role,
                is_primary=payload.is_primary,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_shifts(self) -> list[WorkShift]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_shifts(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_shift(self, payload: WorkShiftCreate) -> WorkShift:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        employee_id = UUID(payload.employee_id)
        assignment_id = UUID(payload.assignment_id) if payload.assignment_id else None
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        if payload.planned_end_at <= payload.planned_start_at:
            raise BadRequestException(code="INVALID_SHIFT_TIME_RANGE", message="Waktu shift tidak valid.")
        employee = await self.repository.get_employee_by_id(employee_id)
        if employee is None or employee.tenant_id != tenant_id:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee shift tidak ditemukan.")
        if assignment_id is not None:
            assignment = await self.repository.get_assignment_by_id(assignment_id)
            if assignment is None or assignment.employee_id != employee_id or assignment.sppg_id != sppg_id:
                raise NotFoundException(code="EMPLOYEE_ASSIGNMENT_NOT_FOUND", message="Assignment employee shift tidak ditemukan.")
        return await self.repository.add_shift(
            WorkShift(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                employee_id=employee_id,
                assignment_id=assignment_id,
                shift_date=payload.shift_date,
                shift_name=payload.shift_name,
                planned_start_at=payload.planned_start_at,
                planned_end_at=payload.planned_end_at,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def list_attendances(self) -> list[Attendance]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_attendances(tenant_id=tenant_id, sppg_id=sppg_id)

    async def record_attendance(self, payload: AttendanceCreate) -> Attendance:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        employee_id = UUID(payload.employee_id)
        shift_id = UUID(payload.shift_id) if payload.shift_id else None
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        employee = await self.repository.get_employee_by_id(employee_id)
        if employee is None or employee.tenant_id != tenant_id:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee attendance tidak ditemukan.")
        worked_hours = 0.0
        if payload.check_in_at and payload.check_out_at:
            if payload.check_out_at < payload.check_in_at:
                raise BadRequestException(code="INVALID_ATTENDANCE_TIME_RANGE", message="Waktu attendance tidak valid.")
            worked_hours = round((payload.check_out_at - payload.check_in_at).total_seconds() / 3600, 6)
        if shift_id is not None:
            shift = await self.repository.get_shift_by_id(shift_id)
            if shift is None or shift.employee_id != employee_id or shift.sppg_id != sppg_id:
                raise NotFoundException(code="WORK_SHIFT_NOT_FOUND", message="Shift attendance tidak ditemukan.")
        return await self.repository.add_attendance(
            Attendance(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                employee_id=employee_id,
                shift_id=shift_id,
                check_in_at=payload.check_in_at,
                check_out_at=payload.check_out_at,
                attendance_status=payload.attendance_status,
                worked_hours=worked_hours,
                notes=payload.notes,
            )
        )

    async def list_timesheets(self) -> list[Timesheet]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_timesheets(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_timesheet(self, payload: TimesheetCreate) -> Timesheet:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        employee_id = UUID(payload.employee_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        if payload.period_end < payload.period_start:
            raise BadRequestException(code="INVALID_TIMESHEET_PERIOD", message="Periode timesheet tidak valid.")
        employee = await self.repository.get_employee_by_id(employee_id)
        if employee is None or employee.tenant_id != tenant_id:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee timesheet tidak ditemukan.")
        return await self.repository.add_timesheet(
            Timesheet(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                employee_id=employee_id,
                period_start=payload.period_start,
                period_end=payload.period_end,
                total_days=payload.total_days,
                total_hours=payload.total_hours,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def list_labor_costs(self) -> list[LaborCost]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_labor_costs(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_labor_cost(self, payload: LaborCostCreate) -> LaborCost:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        employee_id = UUID(payload.employee_id)
        timesheet_id = UUID(payload.timesheet_id) if payload.timesheet_id else None
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        employee = await self.repository.get_employee_by_id(employee_id)
        if employee is None or employee.tenant_id != tenant_id:
            raise NotFoundException(code="EMPLOYEE_NOT_FOUND", message="Employee labor cost tidak ditemukan.")
        if payload.hours_worked < 0 or payload.hourly_rate < 0:
            raise BadRequestException(code="INVALID_LABOR_COST_VALUE", message="Nilai labor cost tidak valid.")
        if timesheet_id is not None:
            timesheet = await self.repository.get_timesheet_by_id(timesheet_id)
            if timesheet is None or timesheet.employee_id != employee_id or timesheet.sppg_id != sppg_id:
                raise NotFoundException(code="TIMESHEET_NOT_FOUND", message="Timesheet labor cost tidak ditemukan.")
        return await self.repository.add_labor_cost(
            LaborCost(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                employee_id=employee_id,
                timesheet_id=timesheet_id,
                cost_date=payload.cost_date,
                cost_component=payload.cost_component,
                hours_worked=payload.hours_worked,
                hourly_rate=payload.hourly_rate,
                total_cost=round(payload.hours_worked * payload.hourly_rate, 6),
                notes=payload.notes,
            )
        )
