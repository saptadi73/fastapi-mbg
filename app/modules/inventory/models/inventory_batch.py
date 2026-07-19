from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryBatch(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "inventory_batches"
    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", "batch_number", name="uq_inventory_batches_tenant_product_batch"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    supplier_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True, index=True)
    warehouse_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True, index=True)
    location_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True, index=True)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    production_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quality_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    quantity_reserved: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    quantity_available: Mapped[float] = mapped_column(Float, nullable=False, default=0)
