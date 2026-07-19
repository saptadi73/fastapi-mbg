from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SupplierPayment(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "supplier_payments"
    __table_args__ = (
        UniqueConstraint("tenant_id", "payment_number", name="uq_supplier_payments_tenant_payment_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    supplier_invoice_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("supplier_invoices.id"),
        nullable=False,
        index=True,
    )
    bank_account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="POSTED")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
