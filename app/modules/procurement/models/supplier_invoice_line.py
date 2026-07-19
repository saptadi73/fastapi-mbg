from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SupplierInvoiceLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "supplier_invoice_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    supplier_invoice_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("supplier_invoices.id"), nullable=False, index=True)
    goods_receipt_line_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goods_receipt_lines.id"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    uom_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uoms.id"), nullable=False)
    invoiced_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
