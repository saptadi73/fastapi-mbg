from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SppgRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    address: str
    province: str | None
    city: str
    district: str | None
    village: str | None
    latitude: float
    longitude: float
    service_radius_meter: float
    timezone: str
    is_active: bool


class SppgCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    address: str
    province: str | None = None
    city: str
    district: str | None = None
    village: str | None = None
    latitude: float
    longitude: float
    service_radius_meter: float = 3000
    timezone: str = "Asia/Jakarta"
    is_active: bool = True
