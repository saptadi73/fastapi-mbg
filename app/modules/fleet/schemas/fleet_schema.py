from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VehicleTypeCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    description: str | None = None
    capacity_portions: int | None = None
    capacity_kg: float | None = None
    temperature_controlled: bool = False
    is_active: bool = True


class VehicleCreate(BaseModel):
    tenant_id: str
    home_sppg_id: str | None = None
    vehicle_type_id: str | None = None
    vehicle_code: str
    plate_number: str
    ownership_status: str = "OWNED"
    brand_name: str | None = None
    model_name: str | None = None
    manufacture_year: int | None = None
    capacity_portions: int | None = None
    fuel_type: str | None = None
    status: str = "ACTIVE"
    is_active: bool = True
    notes: str | None = None


class DriverCreate(BaseModel):
    tenant_id: str
    driver_code: str
    full_name: str
    phone_number: str | None = None
    license_number: str
    license_type: str | None = None
    license_expiry_date: date | None = None
    status: str = "ACTIVE"
    is_active: bool = True
    notes: str | None = None


class VehicleAssignmentCreate(BaseModel):
    sppg_id: str
    driver_id: str | None = None
    assignment_date: date
    end_date: date | None = None
    assignment_role: str = "DELIVERY"
    status: str = "ASSIGNED"
    is_active: bool = True
    notes: str | None = None


class VehicleMaintenanceCreate(BaseModel):
    sppg_id: str | None = None
    maintenance_date: date
    maintenance_type: str
    odometer_km: float | None = None
    cost_amount: float | None = None
    vendor_name: str | None = None
    status: str = "COMPLETED"
    notes: str | None = None


class VehicleTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: str | None
    capacity_portions: int | None
    capacity_kg: float | None
    temperature_controlled: bool
    is_active: bool


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    home_sppg_id: UUID | None
    vehicle_type_id: UUID | None
    vehicle_code: str
    plate_number: str
    ownership_status: str
    brand_name: str | None
    model_name: str | None
    manufacture_year: int | None
    capacity_portions: int | None
    fuel_type: str | None
    status: str
    is_active: bool
    notes: str | None


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    driver_code: str
    full_name: str
    phone_number: str | None
    license_number: str
    license_type: str | None
    license_expiry_date: date | None
    status: str
    is_active: bool
    notes: str | None


class VehicleAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    vehicle_id: UUID
    driver_id: UUID | None
    assignment_date: date
    end_date: date | None
    assignment_role: str
    status: str
    is_active: bool
    notes: str | None


class VehicleMaintenanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    vehicle_id: UUID
    maintenance_date: date
    maintenance_type: str
    odometer_km: float | None
    cost_amount: float | None
    vendor_name: str | None
    status: str
    notes: str | None


class VehicleBundleRead(BaseModel):
    vehicle: VehicleRead
    assignments: list[VehicleAssignmentRead]
    maintenances: list[VehicleMaintenanceRead]
