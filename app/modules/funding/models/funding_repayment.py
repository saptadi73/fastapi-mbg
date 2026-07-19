from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class FundingRepayment(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "funding_repayments"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    agreement_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("funding_agreements.id"), nullable=False, index=True)
    journal_entry_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True, index=True)
    repayment_date: Mapped[date] = mapped_column(Date, nullable=False)
    principal_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    penalty_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    payment_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="POSTED", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
