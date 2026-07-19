from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InventoryBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    warehouse_id: UUID
    product_id: UUID
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float
    average_cost: float


class InventoryTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    transaction_type: str
    reference_type: str | None
    reference_id: UUID | None
    product_id: UUID
    source_warehouse_id: UUID | None
    destination_warehouse_id: UUID | None
    quantity: float
    uom_id: UUID
    unit_cost: float
    total_cost: float
    transaction_at: datetime
    posted_by: UUID
    notes: str | None


class InventoryTransactionCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    transaction_type: str
    reference_type: str | None = None
    reference_id: str | None = None
    product_id: str
    source_warehouse_id: str | None = None
    destination_warehouse_id: str | None = None
    quantity: float
    uom_id: str
    unit_cost: float = 0
    transaction_at: datetime
    notes: str | None = None
