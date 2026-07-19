from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InventoryBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    warehouse_id: UUID
    location_id: UUID | None = None
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
    batch_id: UUID | None = None
    source_warehouse_id: UUID | None
    destination_warehouse_id: UUID | None
    source_location_id: UUID | None = None
    destination_location_id: UUID | None = None
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
    batch_id: str | None = None
    source_warehouse_id: str | None = None
    destination_warehouse_id: str | None = None
    source_location_id: str | None = None
    destination_location_id: str | None = None
    quantity: float
    uom_id: str
    unit_cost: float = 0
    transaction_at: datetime
    notes: str | None = None


class StockLocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    warehouse_id: UUID
    sppg_id: UUID | None
    parent_id: UUID | None
    code: str
    name: str
    location_type: str
    is_active: bool


class StockLocationCreate(BaseModel):
    tenant_id: str
    warehouse_id: str
    sppg_id: str | None = None
    parent_id: str | None = None
    code: str
    name: str
    location_type: str = "WAREHOUSE"
    is_active: bool = True


class InventoryBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    product_id: UUID
    supplier_id: UUID | None
    warehouse_id: UUID | None
    location_id: UUID | None
    batch_number: str
    production_date: date | None
    received_date: date | None
    expiry_date: date | None
    quality_status: str
    is_blocked: bool
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float


class InventoryBatchCreate(BaseModel):
    tenant_id: str
    product_id: str
    supplier_id: str | None = None
    warehouse_id: str | None = None
    location_id: str | None = None
    batch_number: str
    production_date: date | None = None
    received_date: date | None = None
    expiry_date: date | None = None
    quality_status: str = "PENDING"
    is_blocked: bool = False
    quantity_on_hand: float = 0


class FEFOIssuePreviewRequest(BaseModel):
    tenant_id: str
    product_id: str
    warehouse_id: str | None = None
    required_quantity: float


class FEFOIssueCandidateRead(BaseModel):
    batch_id: UUID
    batch_number: str
    expiry_date: date | None
    available_quantity: float
    issue_quantity: float


class FEFOIssuePreviewRead(BaseModel):
    product_id: UUID
    warehouse_id: UUID | None
    required_quantity: float
    fulfilled_quantity: float
    shortage_quantity: float
    candidates: list[FEFOIssueCandidateRead]
