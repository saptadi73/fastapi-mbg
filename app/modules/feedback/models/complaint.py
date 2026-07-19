from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Complaint(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "complaints"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    feedback_submission_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feedback_submissions.id"),
        nullable=True,
        index=True,
    )
    complaint_date: Mapped[datetime] = mapped_column(nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="MEDIUM", index=True)
    complaint_text: Mapped[str] = mapped_column(String(2000), nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN", index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
