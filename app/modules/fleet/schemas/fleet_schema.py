from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class VehicleLocationCreate(BaseModel):
    sppg_id: str | None = None
    assignment_id: str | None = None
    recorded_at: datetime
    latitude: float
    longitude: float
    speed_kph: float | None = None
    heading_degree: float | None = None
    accuracy_meter: float | None = None
    engine_on: bool = True
    movement_status: str = "IDLE"
    event_type: str = "PING"
    source: str | None = None
    address_label: str | None = None
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


class VehicleListRead(VehicleRead):
    driver_id: UUID | None = None
    driver_name: str | None = None
    assignment_role: str | None = None


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
    driver_name: str | None = None
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


class VehicleLocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    vehicle_id: UUID
    assignment_id: UUID | None
    recorded_at: datetime
    latitude: float
    longitude: float
    speed_kph: float | None
    heading_degree: float | None
    accuracy_meter: float | None
    engine_on: bool
    movement_status: str
    event_type: str
    source: str | None
    address_label: str | None
    notes: str | None


class VehicleLocationMapRead(BaseModel):
    vehicle_id: UUID
    vehicle_code: str
    plate_number: str
    home_sppg_id: UUID | None
    driver_id: UUID | None
    driver_name: str | None
    assignment_id: UUID | None
    assignment_role: str | None
    status: str
    latest_location: VehicleLocationRead | None


class VehicleBundleRead(BaseModel):
    vehicle: VehicleRead
    assignments: list[VehicleAssignmentRead]
    maintenances: list[VehicleMaintenanceRead]
    current_location: VehicleLocationRead | None = None
    recent_locations: list[VehicleLocationRead] = Field(default_factory=list)
