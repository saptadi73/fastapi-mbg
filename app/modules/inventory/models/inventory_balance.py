from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryBalance(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "warehouse_id", "product_id", name="uq_inventory_balances_tenant_wh_product"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True)
    location_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True, index=True)
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    quantity_reserved: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    quantity_available: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    average_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
