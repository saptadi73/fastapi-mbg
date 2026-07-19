from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class FundingAgreement(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "funding_agreements"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    funding_source_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("funding_sources.id"),
        nullable=False,
        index=True,
    )
    agreement_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    principal_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    margin_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    fixed_margin_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    disbursement_schedule: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    repayment_terms: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
