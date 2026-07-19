from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
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


class SupplierInvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    goods_receipt_id: UUID
    budget_account_id: UUID | None
    invoice_number: str
    invoice_date: date
    due_date: date | None
    status: str
    total_amount: float
    notes: str | None


class SupplierInvoiceLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    supplier_invoice_id: UUID
    goods_receipt_line_id: UUID | None
    product_id: UUID
    uom_id: UUID
    invoiced_quantity: float
    unit_price: float
    total_amount: float
    description: str | None


class SupplierInvoiceCreateFromGoodsReceipt(BaseModel):
    invoice_date: date
    due_date: date | None = None
    budget_account_id: str | None = None
    notes: str | None = None


class SupplierInvoiceBundleRead(BaseModel):
    supplier_invoice: SupplierInvoiceRead
    lines: list[SupplierInvoiceLineRead]


class SupplierPaymentCreateFromInvoice(BaseModel):
    payment_date: date
    bank_account_id: str | None = None
    notes: str | None = None


class SupplierPaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    supplier_invoice_id: UUID
    bank_account_id: UUID | None
    payment_number: str
    payment_date: date
    status: str
    total_amount: float
    notes: str | None


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    supplier_type: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    city: str | None
    is_active: bool
    is_verified: bool


class SupplierCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    supplier_type: str = "VENDOR"
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    is_active: bool = True
    is_verified: bool = False


class SupplierProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    supplier_id: UUID
    product_id: UUID
    purchase_uom_id: UUID
    supplier_product_code: str | None
    minimum_order_qty: float
    lead_time_days: int
    is_preferred: bool
    is_active: bool


class SupplierProductCreate(BaseModel):
    tenant_id: str
    supplier_id: str
    product_id: str
    purchase_uom_id: str
    supplier_product_code: str | None = None
    minimum_order_qty: float = 0
    lead_time_days: int = 0
    is_preferred: bool = False
    is_active: bool = True


class SupplierPriceHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    supplier_product_id: UUID
    price: float
    effective_from: date
    effective_to: date | None


class SupplierPriceHistoryCreate(BaseModel):
    tenant_id: str
    supplier_product_id: str
    price: float
    effective_from: date
    effective_to: date | None = None


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    supplier_id: UUID
    purchase_request_id: UUID | None
    order_number: str
    order_type: str
    order_date: date
    expected_date: date | None
    status: str
    notes: str | None


class PurchaseOrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    purchase_order_id: UUID
    purchase_request_line_id: UUID | None
    product_id: UUID
    uom_id: UUID
    ordered_quantity: float
    unit_price: float
    total_amount: float
    line_status: str


class PurchaseOrderCreateFromRequest(BaseModel):
    supplier_id: str
    order_date: date
    expected_date: date | None = None
    order_type: str = "PO"
    notes: str | None = None


class PurchaseOrderBundleRead(BaseModel):
    purchase_order: PurchaseOrderRead
    lines: list[PurchaseOrderLineRead]


class GoodsReceiptCreateFromPurchaseOrder(BaseModel):
    warehouse_id: str
    location_id: str | None = None
    receipt_date: date
    notes: str | None = None
    batch_details: list[dict] = Field(default_factory=list)
