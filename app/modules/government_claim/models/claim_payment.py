from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClaimPayment(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "claim_payments"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    claim_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("government_claims.id"), nullable=False, index=True)
    journal_entry_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
