from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class StockLocation(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "stock_locations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "warehouse_id", "code", name="uq_stock_locations_tenant_warehouse_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    parent_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str] = mapped_column(String(50), nullable=False, default="WAREHOUSE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
