from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    symbol: str
    dimension: str
    factor_to_base: float
    is_active: bool


class UomCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    symbol: str
    dimension: str
    factor_to_base: float = 1.0
    is_active: bool = True
