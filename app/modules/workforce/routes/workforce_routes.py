from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workforce.repositories.workforce_repository import WorkforceRepository
from app.modules.workforce.schemas.workforce_schema import (
    AttendanceCreate,
    AttendanceRead,
    EmployeeAssignmentCreate,
    EmployeeAssignmentRead,
    EmployeeBundleRead,
    EmployeeCreate,
    EmployeeRead,
    LaborCostCreate,
    LaborCostRead,
    PositionCreate,
    PositionRead,
    TimesheetCreate,
    TimesheetRead,
    WorkShiftCreate,
    WorkShiftRead,
)
from app.modules.workforce.services.workforce_service import WorkforceService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_workforce_service(session: AsyncSession = Depends(get_db_session)) -> WorkforceService:
    return WorkforceService(
        WorkforceRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/positions")
async def list_positions(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [PositionRead.model_validate(item) for item in await service.list_positions()]
    return success_response(
        code="POSITION_LIST_FOUND",
        message="Daftar posisi berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/positions", status_code=status.HTTP_201_CREATED)
async def create_position(
    payload: PositionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_workforce_service(session)
    position = await service.create_position(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="CREATE_POSITION",
        summary="Posisi workforce dibuat.",
        actor=actor,
        tenant_id=position.tenant_id,
        entity_type="position",
        entity_id=position.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": position.code},
    )
    await session.commit()
    return success_response(
        code="POSITION_CREATED",
        message="Posisi berhasil dibuat.",
        data=PositionRead.model_validate(position),
        meta={"request_id": request.state.request_id},
    )


@router.get("/employees")
async def list_employees(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [EmployeeRead.model_validate(item) for item in await service.list_employees()]
    return success_response(
        code="EMPLOYEE_LIST_FOUND",
        message="Daftar employee berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/employees/{employee_id}")
async def get_employee_detail(
    employee_id: UUID,
    request: Request,
    service: WorkforceService = Depends(get_workforce_service),
) -> dict:
    bundle = await service.get_employee_bundle(employee_id)
    return success_response(
        code="EMPLOYEE_FOUND",
        message="Detail employee berhasil diambil.",
        data=EmployeeBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/employees", status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_workforce_service(session)
    employee = await service.create_employee(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="CREATE_EMPLOYEE",
        summary="Employee workforce dibuat.",
        actor=actor,
        tenant_id=employee.tenant_id,
        entity_type="employee",
        entity_id=employee.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"employee_code": employee.employee_code},
    )
    await session.commit()
    return success_response(
        code="EMPLOYEE_CREATED",
        message="Employee berhasil dibuat.",
        data=EmployeeRead.model_validate(employee),
        meta={"request_id": request.state.request_id},
    )


@router.post("/employees/{employee_id}/assignments", status_code=status.HTTP_201_CREATED)
async def assign_employee(
    employee_id: UUID,
    payload: EmployeeAssignmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_workforce_service(session)
    assignment = await service.assign_employee(employee_id, payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="ASSIGN_EMPLOYEE",
        summary="Employee diassign ke SPPG.",
        actor=actor,
        tenant_id=assignment.tenant_id,
        sppg_id=assignment.sppg_id,
        entity_type="employee_assignment",
        entity_id=assignment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"assignment_role": assignment.assignment_role},
    )
    await session.commit()
    return success_response(
        code="EMPLOYEE_ASSIGNED",
        message="Assignment employee berhasil dibuat.",
        data=EmployeeAssignmentRead.model_validate(assignment),
        meta={"request_id": request.state.request_id},
    )


@router.get("/shifts")
async def list_shifts(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [WorkShiftRead.model_validate(item) for item in await service.list_shifts()]
    return success_response(
        code="WORK_SHIFT_LIST_FOUND",
        message="Daftar shift berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/shifts", status_code=status.HTTP_201_CREATED)
async def create_shift(
    payload: WorkShiftCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_workforce_service(session)
    shift = await service.create_shift(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="CREATE_SHIFT",
        summary="Shift workforce dibuat.",
        actor=actor,
        tenant_id=shift.tenant_id,
        sppg_id=shift.sppg_id,
        entity_type="work_shift",
        entity_id=shift.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"shift_name": shift.shift_name},
    )
    await session.commit()
    return success_response(
        code="WORK_SHIFT_CREATED",
        message="Shift berhasil dibuat.",
        data=WorkShiftRead.model_validate(shift),
        meta={"request_id": request.state.request_id},
    )


@router.get("/attendance")
async def list_attendances(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [AttendanceRead.model_validate(item) for item in await service.list_attendances()]
    return success_response(
        code="ATTENDANCE_LIST_FOUND",
        message="Daftar attendance berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/attendance", status_code=status.HTTP_201_CREATED)
async def create_attendance(
    payload: AttendanceCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_workforce_service(session)
    attendance = await service.record_attendance(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="RECORD_ATTENDANCE",
        summary="Attendance workforce dicatat.",
        actor=actor,
        tenant_id=attendance.tenant_id,
        sppg_id=attendance.sppg_id,
        entity_type="attendance",
        entity_id=attendance.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"attendance_status": attendance.attendance_status, "worked_hours": attendance.worked_hours},
    )
    await session.commit()
    return success_response(
        code="ATTENDANCE_RECORDED",
        message="Attendance berhasil dicatat.",
        data=AttendanceRead.model_validate(attendance),
        meta={"request_id": request.state.request_id},
    )


@router.get("/timesheets")
async def list_timesheets(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [TimesheetRead.model_validate(item) for item in await service.list_timesheets()]
    return success_response(
        code="TIMESHEET_LIST_FOUND",
        message="Daftar timesheet berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/timesheets", status_code=status.HTTP_201_CREATED)
async def create_timesheet(
    payload: TimesheetCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "finance_manager")),
) -> dict:
    service = get_workforce_service(session)
    timesheet = await service.create_timesheet(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="CREATE_TIMESHEET",
        summary="Timesheet workforce dibuat.",
        actor=actor,
        tenant_id=timesheet.tenant_id,
        sppg_id=timesheet.sppg_id,
        entity_type="timesheet",
        entity_id=timesheet.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"total_hours": timesheet.total_hours},
    )
    await session.commit()
    return success_response(
        code="TIMESHEET_CREATED",
        message="Timesheet berhasil dibuat.",
        data=TimesheetRead.model_validate(timesheet),
        meta={"request_id": request.state.request_id},
    )


@router.get("/labor-costs")
async def list_labor_costs(request: Request, service: WorkforceService = Depends(get_workforce_service)) -> dict:
    items = [LaborCostRead.model_validate(item) for item in await service.list_labor_costs()]
    return success_response(
        code="LABOR_COST_LIST_FOUND",
        message="Daftar labor cost berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/labor-costs", status_code=status.HTTP_201_CREATED)
async def create_labor_cost(
    payload: LaborCostCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "finance_manager")),
) -> dict:
    service = get_workforce_service(session)
    labor_cost = await service.create_labor_cost(payload)
    await get_audit_service(session).record_event(
        event_type="WORKFORCE",
        module_name="workforce",
        action_name="CREATE_LABOR_COST",
        summary="Labor cost workforce dicatat.",
        actor=actor,
        tenant_id=labor_cost.tenant_id,
        sppg_id=labor_cost.sppg_id,
        entity_type="labor_cost",
        entity_id=labor_cost.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"total_cost": labor_cost.total_cost},
    )
    await session.commit()
    return success_response(
        code="LABOR_COST_CREATED",
        message="Labor cost berhasil dicatat.",
        data=LaborCostRead.model_validate(labor_cost),
        meta={"request_id": request.state.request_id},
    )
