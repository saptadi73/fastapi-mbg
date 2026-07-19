from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class QCInspectionLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "qc_inspection_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    inspection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qc_inspections.id"),
        nullable=False,
        index=True,
    )
    parameter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actual_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    result_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PASS")
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
