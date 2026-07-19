from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SppgRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    city: str
    latitude: float
    longitude: float


class SppgCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    city: str
    latitude: float
    longitude: float
