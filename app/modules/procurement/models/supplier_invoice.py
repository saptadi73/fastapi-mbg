from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SupplierInvoice(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "supplier_invoices"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_number", name="uq_supplier_invoices_tenant_invoice_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    goods_receipt_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goods_receipts.id"), nullable=False, index=True)
    budget_account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="POSTED")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
