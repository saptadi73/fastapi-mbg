from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PurchaseOrder(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "order_number", name="uq_purchase_orders_tenant_order_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    supplier_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    purchase_request_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requests.id"),
        nullable=True,
        index=True,
    )
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False, default="PO")
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
