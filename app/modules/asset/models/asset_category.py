from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AssetCategory(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "asset_categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_asset_categories_tenant_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True)
    depreciation_expense_account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True)
    accumulated_depreciation_account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True)
    useful_life_months: Mapped[int | None] = mapped_column(nullable=True)
    depreciation_method: Mapped[str] = mapped_column(String(50), nullable=False, default="STRAIGHT_LINE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
