from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Asset(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("tenant_id", "asset_code", name="uq_assets_tenant_asset_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    asset_category_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("asset_categories.id"), nullable=True, index=True)
    asset_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    acquisition_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    acquisition_cost: Mapped[float] = mapped_column(nullable=False, default=0)
    residual_value: Mapped[float] = mapped_column(nullable=False, default=0)
    useful_life_months: Mapped[int | None] = mapped_column(nullable=True)
    depreciation_method: Mapped[str] = mapped_column(String(50), nullable=False, default="STRAIGHT_LINE")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
