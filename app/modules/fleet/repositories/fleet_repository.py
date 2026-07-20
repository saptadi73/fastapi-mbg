from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fleet.models.driver import Driver
from app.modules.fleet.models.vehicle import Vehicle
from app.modules.fleet.models.vehicle_assignment import VehicleAssignment
from app.modules.fleet.models.vehicle_location import VehicleLocation
from app.modules.fleet.models.vehicle_maintenance import VehicleMaintenance
from app.modules.fleet.models.vehicle_type import VehicleType


class FleetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_vehicle_types(self, tenant_id: UUID | None = None) -> list[VehicleType]:
        query = select(VehicleType).order_by(VehicleType.name)
        if tenant_id is not None:
            query = query.where(VehicleType.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_vehicle_type_by_id(self, vehicle_type_id: UUID) -> VehicleType | None:
        return await self.session.get(VehicleType, vehicle_type_id)

    async def get_vehicle_type_by_tenant_code(self, tenant_id: UUID, code: str) -> VehicleType | None:
        result = await self.session.execute(
            select(VehicleType).where(VehicleType.tenant_id == tenant_id, VehicleType.code == code)
        )
        return result.scalar_one_or_none()

    async def add_vehicle_type(self, vehicle_type: VehicleType) -> VehicleType:
        self.session.add(vehicle_type)
        await self.session.flush()
        await self.session.refresh(vehicle_type)
        return vehicle_type

    async def list_vehicles(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Vehicle]:
        query = select(Vehicle).order_by(Vehicle.vehicle_code)
        if tenant_id is not None:
            query = query.where(Vehicle.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Vehicle.home_sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_vehicle_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return await self.session.get(Vehicle, vehicle_id)

    async def get_vehicle_by_id_and_scope(
        self,
        vehicle_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> Vehicle | None:
        query = select(Vehicle).where(Vehicle.id == vehicle_id)
        if tenant_id is not None:
            query = query.where(Vehicle.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Vehicle.home_sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_vehicle_by_tenant_code(self, tenant_id: UUID, vehicle_code: str) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(Vehicle.tenant_id == tenant_id, Vehicle.vehicle_code == vehicle_code)
        )
        return result.scalar_one_or_none()

    async def get_vehicle_by_tenant_plate(self, tenant_id: UUID, plate_number: str) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(Vehicle.tenant_id == tenant_id, Vehicle.plate_number == plate_number)
        )
        return result.scalar_one_or_none()

    async def add_vehicle(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def list_drivers(self, tenant_id: UUID | None = None) -> list[Driver]:
        query = select(Driver).order_by(Driver.full_name)
        if tenant_id is not None:
            query = query.where(Driver.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_driver_by_id(self, driver_id: UUID) -> Driver | None:
        return await self.session.get(Driver, driver_id)

    async def get_driver_by_tenant_code(self, tenant_id: UUID, driver_code: str) -> Driver | None:
        result = await self.session.execute(
            select(Driver).where(Driver.tenant_id == tenant_id, Driver.driver_code == driver_code)
        )
        return result.scalar_one_or_none()

    async def get_driver_by_tenant_license(self, tenant_id: UUID, license_number: str) -> Driver | None:
        result = await self.session.execute(
            select(Driver).where(Driver.tenant_id == tenant_id, Driver.license_number == license_number)
        )
        return result.scalar_one_or_none()

    async def add_driver(self, driver: Driver) -> Driver:
        self.session.add(driver)
        await self.session.flush()
        await self.session.refresh(driver)
        return driver

    async def list_assignments(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[VehicleAssignment]:
        query = select(VehicleAssignment).order_by(VehicleAssignment.assignment_date.desc(), VehicleAssignment.created_at.desc())
        if tenant_id is not None:
            query = query.where(VehicleAssignment.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(VehicleAssignment.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_assignments_by_vehicle(self, vehicle_id: UUID) -> list[VehicleAssignment]:
        result = await self.session.execute(
            select(VehicleAssignment)
            .where(VehicleAssignment.vehicle_id == vehicle_id)
            .order_by(VehicleAssignment.assignment_date.desc(), VehicleAssignment.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_assignment(self, assignment: VehicleAssignment) -> VehicleAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def get_assignment_by_id(self, assignment_id: UUID) -> VehicleAssignment | None:
        return await self.session.get(VehicleAssignment, assignment_id)

    async def list_maintenances(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[VehicleMaintenance]:
        query = select(VehicleMaintenance).order_by(
            VehicleMaintenance.maintenance_date.desc(),
            VehicleMaintenance.created_at.desc(),
        )
        if tenant_id is not None:
            query = query.where(VehicleMaintenance.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(VehicleMaintenance.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_maintenances_by_vehicle(self, vehicle_id: UUID) -> list[VehicleMaintenance]:
        result = await self.session.execute(
            select(VehicleMaintenance)
            .where(VehicleMaintenance.vehicle_id == vehicle_id)
            .order_by(VehicleMaintenance.maintenance_date.desc(), VehicleMaintenance.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_maintenance(self, maintenance: VehicleMaintenance) -> VehicleMaintenance:
        self.session.add(maintenance)
        await self.session.flush()
        await self.session.refresh(maintenance)
        return maintenance

    async def list_vehicle_locations(
        self,
        *,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
        vehicle_id: UUID | None = None,
        limit: int = 50,
    ) -> list[VehicleLocation]:
        query = select(VehicleLocation).order_by(VehicleLocation.recorded_at.desc(), VehicleLocation.created_at.desc())
        if tenant_id is not None:
            query = query.where(VehicleLocation.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(VehicleLocation.sppg_id == sppg_id)
        if vehicle_id is not None:
            query = query.where(VehicleLocation.vehicle_id == vehicle_id)
        result = await self.session.execute(query.limit(limit))
        return list(result.scalars().all())

    async def add_vehicle_location(self, location: VehicleLocation) -> VehicleLocation:
        self.session.add(location)
        await self.session.flush()
        await self.session.refresh(location)
        return location
