from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClaimVerification(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "claim_verifications"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    claim_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("government_claims.id"), nullable=False, index=True)
    verification_date: Mapped[date] = mapped_column(Date, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False)
    verified_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    verifier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
