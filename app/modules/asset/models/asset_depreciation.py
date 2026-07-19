from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AssetDepreciation(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "asset_depreciations"
    __table_args__ = (
        UniqueConstraint("asset_id", "depreciation_date", name="uq_asset_depreciation_asset_date"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    asset_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    journal_entry_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True, index=True)
    depreciation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    depreciation_amount: Mapped[float] = mapped_column(nullable=False, default=0)
    accumulated_depreciation_amount: Mapped[float] = mapped_column(nullable=False, default=0)
    book_value_after: Mapped[float] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="POSTED", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
