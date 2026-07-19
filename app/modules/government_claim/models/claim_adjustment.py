from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClaimAdjustment(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "claim_adjustments"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    claim_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("government_claims.id"), nullable=False, index=True)
    adjustment_date: Mapped[date] = mapped_column(Date, nullable=False)
    adjustment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
