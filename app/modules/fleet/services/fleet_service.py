from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.fleet.models.driver import Driver
from app.modules.fleet.models.vehicle import Vehicle
from app.modules.fleet.models.vehicle_assignment import VehicleAssignment
from app.modules.fleet.models.vehicle_maintenance import VehicleMaintenance
from app.modules.fleet.models.vehicle_type import VehicleType
from app.modules.fleet.repositories.fleet_repository import FleetRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class FleetService:
    def __init__(
        self,
        repository: FleetRepository,
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

    async def list_vehicle_types(self) -> list[VehicleType]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_vehicle_types(tenant_id=tenant_id)

    async def create_vehicle_type(self, payload) -> VehicleType:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant fleet tidak ditemukan.")
        if await self.repository.get_vehicle_type_by_tenant_code(tenant_id, payload.code) is not None:
            raise ConflictException(code="VEHICLE_TYPE_CODE_ALREADY_EXISTS", message="Kode vehicle type sudah digunakan.")
        if payload.capacity_portions is not None and payload.capacity_portions < 0:
            raise BadRequestException(code="INVALID_VEHICLE_TYPE_CAPACITY", message="Kapasitas vehicle type tidak valid.")
        if payload.capacity_kg is not None and payload.capacity_kg < 0:
            raise BadRequestException(code="INVALID_VEHICLE_TYPE_CAPACITY", message="Kapasitas vehicle type tidak valid.")
        return await self.repository.add_vehicle_type(
            VehicleType(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                description=payload.description,
                capacity_portions=payload.capacity_portions,
                capacity_kg=payload.capacity_kg,
                temperature_controlled=payload.temperature_controlled,
                is_active=payload.is_active,
            )
        )

    async def list_vehicles(self) -> list[Vehicle]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_vehicles(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_vehicle_bundle(self, vehicle_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        vehicle = await self.repository.get_vehicle_by_id_and_scope(vehicle_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if vehicle is None:
            raise NotFoundException(code="VEHICLE_NOT_FOUND", message="Vehicle tidak ditemukan.")
        return {
            "vehicle": vehicle,
            "assignments": await self.repository.list_assignments_by_vehicle(vehicle.id),
            "maintenances": await self.repository.list_maintenances_by_vehicle(vehicle.id),
        }

    async def create_vehicle(self, payload) -> Vehicle:
        tenant_id = UUID(payload.tenant_id)
        home_sppg_id = UUID(payload.home_sppg_id) if payload.home_sppg_id else None
        vehicle_type_id = UUID(payload.vehicle_type_id) if payload.vehicle_type_id else None
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant vehicle tidak ditemukan.")
        if await self.repository.get_vehicle_by_tenant_code(tenant_id, payload.vehicle_code) is not None:
            raise ConflictException(code="VEHICLE_CODE_ALREADY_EXISTS", message="Kode vehicle sudah digunakan.")
        if await self.repository.get_vehicle_by_tenant_plate(tenant_id, payload.plate_number) is not None:
            raise ConflictException(code="VEHICLE_PLATE_ALREADY_EXISTS", message="Nomor polisi vehicle sudah digunakan.")
        if home_sppg_id is not None:
            enforce_sppg_write_scope(home_sppg_id)
            sppg = await self.sppg_repository.get_by_id(home_sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG vehicle tidak ditemukan.")
        if vehicle_type_id is not None:
            vehicle_type = await self.repository.get_vehicle_type_by_id(vehicle_type_id)
            if vehicle_type is None or vehicle_type.tenant_id != tenant_id:
                raise NotFoundException(code="VEHICLE_TYPE_NOT_FOUND", message="Vehicle type tidak ditemukan.")
        if payload.capacity_portions is not None and payload.capacity_portions < 0:
            raise BadRequestException(code="INVALID_VEHICLE_CAPACITY", message="Kapasitas vehicle tidak valid.")
        return await self.repository.add_vehicle(
            Vehicle(
                tenant_id=tenant_id,
                home_sppg_id=home_sppg_id,
                vehicle_type_id=vehicle_type_id,
                vehicle_code=payload.vehicle_code,
                plate_number=payload.plate_number,
                ownership_status=payload.ownership_status,
                brand_name=payload.brand_name,
                model_name=payload.model_name,
                manufacture_year=payload.manufacture_year,
                capacity_portions=payload.capacity_portions,
                fuel_type=payload.fuel_type,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_drivers(self) -> list[Driver]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_drivers(tenant_id=tenant_id)

    async def create_driver(self, payload) -> Driver:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant driver tidak ditemukan.")
        if await self.repository.get_driver_by_tenant_code(tenant_id, payload.driver_code) is not None:
            raise ConflictException(code="DRIVER_CODE_ALREADY_EXISTS", message="Kode driver sudah digunakan.")
        if await self.repository.get_driver_by_tenant_license(tenant_id, payload.license_number) is not None:
            raise ConflictException(code="DRIVER_LICENSE_ALREADY_EXISTS", message="Nomor SIM driver sudah digunakan.")
        return await self.repository.add_driver(
            Driver(
                tenant_id=tenant_id,
                driver_code=payload.driver_code,
                full_name=payload.full_name,
                phone_number=payload.phone_number,
                license_number=payload.license_number,
                license_type=payload.license_type,
                license_expiry_date=payload.license_expiry_date,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_assignments(self) -> list[VehicleAssignment]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_assignments(tenant_id=tenant_id, sppg_id=sppg_id)

    async def assign_vehicle(self, vehicle_id: UUID, payload) -> VehicleAssignment:
        vehicle = await self.repository.get_vehicle_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException(code="VEHICLE_NOT_FOUND", message="Vehicle tidak ditemukan.")
        sppg_id = UUID(payload.sppg_id)
        driver_id = UUID(payload.driver_id) if payload.driver_id else None
        enforce_tenant_write_scope(vehicle.tenant_id)
        enforce_sppg_write_scope(sppg_id)
        if payload.end_date and payload.end_date < payload.assignment_date:
            raise BadRequestException(code="INVALID_VEHICLE_ASSIGNMENT_DATE_RANGE", message="Tanggal assignment vehicle tidak valid.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != vehicle.tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG assignment vehicle tidak ditemukan.")
        if driver_id is not None:
            driver = await self.repository.get_driver_by_id(driver_id)
            if driver is None or driver.tenant_id != vehicle.tenant_id:
                raise NotFoundException(code="DRIVER_NOT_FOUND", message="Driver assignment vehicle tidak ditemukan.")
        return await self.repository.add_assignment(
            VehicleAssignment(
                tenant_id=vehicle.tenant_id,
                sppg_id=sppg_id,
                vehicle_id=vehicle.id,
                driver_id=driver_id,
                assignment_date=payload.assignment_date,
                end_date=payload.end_date,
                assignment_role=payload.assignment_role,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_maintenances(self) -> list[VehicleMaintenance]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_maintenances(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_maintenance(self, vehicle_id: UUID, payload) -> VehicleMaintenance:
        vehicle = await self.repository.get_vehicle_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundException(code="VEHICLE_NOT_FOUND", message="Vehicle tidak ditemukan.")
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        enforce_tenant_write_scope(vehicle.tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != vehicle.tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG maintenance vehicle tidak ditemukan.")
        if payload.odometer_km is not None and payload.odometer_km < 0:
            raise BadRequestException(code="INVALID_VEHICLE_ODOMETER", message="Nilai odometer vehicle tidak valid.")
        if payload.cost_amount is not None and payload.cost_amount < 0:
            raise BadRequestException(code="INVALID_VEHICLE_MAINTENANCE_COST", message="Biaya maintenance vehicle tidak valid.")
        return await self.repository.add_maintenance(
            VehicleMaintenance(
                tenant_id=vehicle.tenant_id,
                sppg_id=sppg_id,
                vehicle_id=vehicle.id,
                maintenance_date=payload.maintenance_date,
                maintenance_type=payload.maintenance_type,
                odometer_km=payload.odometer_km,
                cost_amount=payload.cost_amount,
                vendor_name=payload.vendor_name,
                status=payload.status,
                notes=payload.notes,
            )
        )
