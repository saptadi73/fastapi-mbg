from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workforce.models.attendance import Attendance
from app.modules.workforce.models.employee import Employee
from app.modules.workforce.models.employee_assignment import EmployeeAssignment
from app.modules.workforce.models.labor_cost import LaborCost
from app.modules.workforce.models.position import Position
from app.modules.workforce.models.timesheet import Timesheet
from app.modules.workforce.models.work_shift import WorkShift


class WorkforceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_positions(self, tenant_id: UUID | None = None) -> list[Position]:
        query = select(Position).order_by(Position.name)
        if tenant_id is not None:
            query = query.where(Position.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_position_by_id(self, position_id: UUID) -> Position | None:
        return await self.session.get(Position, position_id)

    async def get_position_by_tenant_code(self, tenant_id: UUID, code: str) -> Position | None:
        result = await self.session.execute(
            select(Position).where(Position.tenant_id == tenant_id, Position.code == code)
        )
        return result.scalar_one_or_none()

    async def add_position(self, position: Position) -> Position:
        self.session.add(position)
        await self.session.flush()
        await self.session.refresh(position)
        return position

    async def list_employees(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Employee]:
        query = select(Employee).order_by(Employee.full_name)
        if tenant_id is not None:
            query = query.where(Employee.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(
                Employee.id.in_(
                    select(EmployeeAssignment.employee_id).where(EmployeeAssignment.sppg_id == sppg_id)
                )
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_employee_by_id(self, employee_id: UUID) -> Employee | None:
        return await self.session.get(Employee, employee_id)

    async def get_employee_by_id_and_scope(self, employee_id: UUID, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> Employee | None:
        query = select(Employee).where(Employee.id == employee_id)
        if tenant_id is not None:
            query = query.where(Employee.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(
                Employee.id.in_(
                    select(EmployeeAssignment.employee_id).where(EmployeeAssignment.sppg_id == sppg_id)
                )
            )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_employee_by_tenant_code(self, tenant_id: UUID, employee_code: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.tenant_id == tenant_id, Employee.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    async def add_employee(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        await self.session.refresh(employee)
        return employee

    async def list_assignments(self, employee_id: UUID) -> list[EmployeeAssignment]:
        result = await self.session.execute(
            select(EmployeeAssignment)
            .where(EmployeeAssignment.employee_id == employee_id)
            .order_by(EmployeeAssignment.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_assignment_by_employee_and_sppg(self, employee_id: UUID, sppg_id: UUID) -> EmployeeAssignment | None:
        result = await self.session.execute(
            select(EmployeeAssignment).where(
                EmployeeAssignment.employee_id == employee_id,
                EmployeeAssignment.sppg_id == sppg_id,
                EmployeeAssignment.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_assignment_by_id(self, assignment_id: UUID) -> EmployeeAssignment | None:
        return await self.session.get(EmployeeAssignment, assignment_id)

    async def add_assignment(self, assignment: EmployeeAssignment) -> EmployeeAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def list_shifts(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[WorkShift]:
        query = select(WorkShift).order_by(WorkShift.shift_date.desc(), WorkShift.planned_start_at.desc())
        if tenant_id is not None:
            query = query.where(WorkShift.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(WorkShift.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_shift(self, shift: WorkShift) -> WorkShift:
        self.session.add(shift)
        await self.session.flush()
        await self.session.refresh(shift)
        return shift

    async def get_shift_by_id(self, shift_id: UUID) -> WorkShift | None:
        return await self.session.get(WorkShift, shift_id)

    async def list_attendances(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Attendance]:
        query = select(Attendance).order_by(Attendance.created_at.desc())
        if tenant_id is not None:
            query = query.where(Attendance.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Attendance.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_attendance(self, attendance: Attendance) -> Attendance:
        self.session.add(attendance)
        await self.session.flush()
        await self.session.refresh(attendance)
        return attendance

    async def list_timesheets(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Timesheet]:
        query = select(Timesheet).order_by(Timesheet.period_start.desc(), Timesheet.created_at.desc())
        if tenant_id is not None:
            query = query.where(Timesheet.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Timesheet.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_timesheet(self, timesheet: Timesheet) -> Timesheet:
        self.session.add(timesheet)
        await self.session.flush()
        await self.session.refresh(timesheet)
        return timesheet

    async def get_timesheet_by_id(self, timesheet_id: UUID) -> Timesheet | None:
        return await self.session.get(Timesheet, timesheet_id)

    async def list_labor_costs(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[LaborCost]:
        query = select(LaborCost).order_by(LaborCost.cost_date.desc(), LaborCost.created_at.desc())
        if tenant_id is not None:
            query = query.where(LaborCost.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(LaborCost.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_labor_costs_by_date(
        self,
        *,
        tenant_id: UUID,
        sppg_id: UUID | None = None,
        cost_date,
    ) -> list[LaborCost]:
        query = select(LaborCost).where(
            LaborCost.tenant_id == tenant_id,
            LaborCost.cost_date == cost_date,
        )
        if sppg_id is not None:
            query = query.where(LaborCost.sppg_id == sppg_id)
        query = query.order_by(LaborCost.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_labor_cost(self, labor_cost: LaborCost) -> LaborCost:
        self.session.add(labor_cost)
        await self.session.flush()
        await self.session.refresh(labor_cost)
        return labor_cost
