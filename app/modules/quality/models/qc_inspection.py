from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class QCInspection(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "qc_inspections"
    __table_args__ = (
        UniqueConstraint("tenant_id", "inspection_number", name="uq_qc_inspections_tenant_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    inspection_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    inspection_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PRODUCTION")
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="PRODUCTION_OUTPUT")
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    inspection_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    inspector_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    overall_result: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_mandatory_for_release: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
