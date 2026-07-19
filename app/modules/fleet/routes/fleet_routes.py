from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.fleet.repositories.fleet_repository import FleetRepository
from app.modules.fleet.schemas.fleet_schema import (
    DriverCreate,
    DriverRead,
    VehicleAssignmentCreate,
    VehicleAssignmentRead,
    VehicleBundleRead,
    VehicleCreate,
    VehicleMaintenanceCreate,
    VehicleMaintenanceRead,
    VehicleRead,
    VehicleTypeCreate,
    VehicleTypeRead,
)
from app.modules.fleet.services.fleet_service import FleetService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_fleet_service(session: AsyncSession = Depends(get_db_session)) -> FleetService:
    return FleetService(
        FleetRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/vehicle-types")
async def list_vehicle_types(request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    items = [VehicleTypeRead.model_validate(item) for item in await service.list_vehicle_types()]
    return success_response(
        code="VEHICLE_TYPE_LIST_FOUND",
        message="Daftar vehicle type berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/vehicle-types", status_code=status.HTTP_201_CREATED)
async def create_vehicle_type(
    payload: VehicleTypeCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_fleet_service(session)
    vehicle_type = await service.create_vehicle_type(payload)
    await get_audit_service(session).record_event(
        event_type="FLEET",
        module_name="fleet",
        action_name="CREATE_VEHICLE_TYPE",
        summary="Vehicle type dibuat.",
        actor=actor,
        tenant_id=vehicle_type.tenant_id,
        entity_type="vehicle_type",
        entity_id=vehicle_type.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": vehicle_type.code},
    )
    await session.commit()
    return success_response(
        code="VEHICLE_TYPE_CREATED",
        message="Vehicle type berhasil dibuat.",
        data=VehicleTypeRead.model_validate(vehicle_type),
        meta={"request_id": request.state.request_id},
    )


@router.get("/vehicles")
async def list_vehicles(request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    items = [VehicleRead.model_validate(item) for item in await service.list_vehicles()]
    return success_response(
        code="VEHICLE_LIST_FOUND",
        message="Daftar vehicle berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/vehicles/{vehicle_id}")
async def get_vehicle_detail(vehicle_id: UUID, request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    bundle = await service.get_vehicle_bundle(vehicle_id)
    return success_response(
        code="VEHICLE_FOUND",
        message="Detail vehicle berhasil diambil.",
        data=VehicleBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    payload: VehicleCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_fleet_service(session)
    vehicle = await service.create_vehicle(payload)
    await get_audit_service(session).record_event(
        event_type="FLEET",
        module_name="fleet",
        action_name="CREATE_VEHICLE",
        summary="Vehicle dibuat.",
        actor=actor,
        tenant_id=vehicle.tenant_id,
        sppg_id=vehicle.home_sppg_id,
        entity_type="vehicle",
        entity_id=vehicle.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"vehicle_code": vehicle.vehicle_code, "plate_number": vehicle.plate_number},
    )
    await session.commit()
    return success_response(
        code="VEHICLE_CREATED",
        message="Vehicle berhasil dibuat.",
        data=VehicleRead.model_validate(vehicle),
        meta={"request_id": request.state.request_id},
    )


@router.get("/drivers")
async def list_drivers(request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    items = [DriverRead.model_validate(item) for item in await service.list_drivers()]
    return success_response(
        code="DRIVER_LIST_FOUND",
        message="Daftar driver berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/drivers", status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_fleet_service(session)
    driver = await service.create_driver(payload)
    await get_audit_service(session).record_event(
        event_type="FLEET",
        module_name="fleet",
        action_name="CREATE_DRIVER",
        summary="Driver fleet dibuat.",
        actor=actor,
        tenant_id=driver.tenant_id,
        entity_type="driver",
        entity_id=driver.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"driver_code": driver.driver_code},
    )
    await session.commit()
    return success_response(
        code="DRIVER_CREATED",
        message="Driver berhasil dibuat.",
        data=DriverRead.model_validate(driver),
        meta={"request_id": request.state.request_id},
    )


@router.get("/assignments")
async def list_assignments(request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    items = [VehicleAssignmentRead.model_validate(item) for item in await service.list_assignments()]
    return success_response(
        code="VEHICLE_ASSIGNMENT_LIST_FOUND",
        message="Daftar assignment vehicle berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/vehicles/{vehicle_id}/assignments", status_code=status.HTTP_201_CREATED)
async def assign_vehicle(
    vehicle_id: UUID,
    payload: VehicleAssignmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_fleet_service(session)
    assignment = await service.assign_vehicle(vehicle_id, payload)
    await get_audit_service(session).record_event(
        event_type="FLEET",
        module_name="fleet",
        action_name="ASSIGN_VEHICLE",
        summary="Vehicle diassign ke SPPG.",
        actor=actor,
        tenant_id=assignment.tenant_id,
        sppg_id=assignment.sppg_id,
        entity_type="vehicle_assignment",
        entity_id=assignment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"assignment_role": assignment.assignment_role},
    )
    await session.commit()
    return success_response(
        code="VEHICLE_ASSIGNED",
        message="Assignment vehicle berhasil dibuat.",
        data=VehicleAssignmentRead.model_validate(assignment),
        meta={"request_id": request.state.request_id},
    )


@router.get("/maintenances")
async def list_maintenances(request: Request, service: FleetService = Depends(get_fleet_service)) -> dict:
    items = [VehicleMaintenanceRead.model_validate(item) for item in await service.list_maintenances()]
    return success_response(
        code="VEHICLE_MAINTENANCE_LIST_FOUND",
        message="Daftar maintenance vehicle berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/vehicles/{vehicle_id}/maintenances", status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    vehicle_id: UUID,
    payload: VehicleMaintenanceCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_fleet_service(session)
    maintenance = await service.create_maintenance(vehicle_id, payload)
    await get_audit_service(session).record_event(
        event_type="FLEET",
        module_name="fleet",
        action_name="CREATE_VEHICLE_MAINTENANCE",
        summary="Maintenance vehicle dicatat.",
        actor=actor,
        tenant_id=maintenance.tenant_id,
        sppg_id=maintenance.sppg_id,
        entity_type="vehicle_maintenance",
        entity_id=maintenance.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"maintenance_type": maintenance.maintenance_type, "cost_amount": maintenance.cost_amount},
    )
    await session.commit()
    return success_response(
        code="VEHICLE_MAINTENANCE_CREATED",
        message="Maintenance vehicle berhasil dicatat.",
        data=VehicleMaintenanceRead.model_validate(maintenance),
        meta={"request_id": request.state.request_id},
    )
