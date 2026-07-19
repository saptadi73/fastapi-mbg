from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Float, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class GovernmentClaim(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "government_claims"
    __table_args__ = (
        UniqueConstraint("tenant_id", "claim_number", name="uq_government_claims_tenant_claim_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    program_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True, index=True)
    claim_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTUAL_COST")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    total_portions: Mapped[int] = mapped_column(nullable=False, default=0)
    claimed_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    approved_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    paid_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    submitted_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    verified_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
