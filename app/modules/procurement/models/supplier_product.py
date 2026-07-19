from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SupplierProduct(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "supplier_products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "supplier_id", "product_id", name="uq_supplier_products_tenant_supplier_product"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    supplier_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    purchase_uom_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uoms.id"), nullable=False)
    supplier_product_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    minimum_order_qty: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_preferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
