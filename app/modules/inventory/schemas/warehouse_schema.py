from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    code: str
    name: str
    warehouse_type: str
    location: str
    is_active: bool


class WarehouseCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    code: str
    name: str
    warehouse_type: str
    location: str
    is_active: bool = True
