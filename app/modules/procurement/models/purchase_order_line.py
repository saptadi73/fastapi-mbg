from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PurchaseOrderLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "purchase_order_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    purchase_order_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.id"),
        nullable=False,
        index=True,
    )
    purchase_request_line_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_request_lines.id"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    uom_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uoms.id"), nullable=False)
    ordered_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    line_status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
