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
    track_batch: bool
    track_expiry: bool
    minimum_stock: float
    maximum_stock: float | None
    reorder_point: float
    valuation_method: str
    is_active: bool


class ProductCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    product_type: str
    stock_uom_id: str
    standard_cost: float = 0
    track_batch: bool = False
    track_expiry: bool = False
    minimum_stock: float = 0
    maximum_stock: float | None = None
    reorder_point: float = 0
    valuation_method: str = "MOVING_AVERAGE"
    is_active: bool = True
