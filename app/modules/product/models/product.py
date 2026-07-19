from sqlalchemy import Boolean, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Product(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_products_tenant_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stock_uom_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uoms.id"), nullable=False)
    standard_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    track_batch: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    track_expiry: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    minimum_stock: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    maximum_stock: Mapped[float | None] = mapped_column(Float, nullable=True)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    valuation_method: Mapped[str] = mapped_column(String(30), nullable=False, default="MOVING_AVERAGE")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
