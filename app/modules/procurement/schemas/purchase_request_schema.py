from uuid import UUID

from pydantic import BaseModel, ConfigDict
from datetime import date


class PurchaseRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    meal_plan_id: UUID | None
    request_number: str
    status: str
    notes: str | None


class PurchaseRequestLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    purchase_request_id: UUID
    product_id: UUID
    uom_id: UUID
    requested_quantity: float
    shortage_quantity: float
    estimated_unit_cost: float
    estimated_total_cost: float


class PurchaseRequestBundleRead(BaseModel):
    purchase_request: PurchaseRequestRead
    lines: list[PurchaseRequestLineRead]


class GoodsReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    purchase_request_id: UUID | None
    warehouse_id: UUID
    receipt_number: str
    receipt_date: date
    status: str
    notes: str | None


class GoodsReceiptLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    goods_receipt_id: UUID
    purchase_request_line_id: UUID | None
    product_id: UUID
    uom_id: UUID
    received_quantity: float
    unit_cost: float
    total_cost: float


class GoodsReceiptCreateFromPurchaseRequest(BaseModel):
    warehouse_id: str
    receipt_date: date
    notes: str | None = None


class GoodsReceiptBundleRead(BaseModel):
    goods_receipt: GoodsReceiptRead
    lines: list[GoodsReceiptLineRead]
