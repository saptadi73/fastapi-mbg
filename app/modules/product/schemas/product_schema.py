from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    product_type: str
    stock_uom_id: UUID
    standard_cost: float
    is_active: bool


class ProductCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    product_type: str
    stock_uom_id: str
    standard_cost: float = 0
    is_active: bool = True
