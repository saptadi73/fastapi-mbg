from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ServiceQualityScore(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "service_quality_scores"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sppg_id", "score_date", name="uq_service_quality_scores_scope_date"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    score_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    acceptance_score: Mapped[float | None] = mapped_column(nullable=True)
    waste_score: Mapped[float | None] = mapped_column(nullable=True)
    delivery_score: Mapped[float | None] = mapped_column(nullable=True)
    temperature_score: Mapped[float | None] = mapped_column(nullable=True)
    taste_score: Mapped[float | None] = mapped_column(nullable=True)
    nutrition_score: Mapped[float | None] = mapped_column(nullable=True)
    complaint_score: Mapped[float | None] = mapped_column(nullable=True)
    total_score: Mapped[float] = mapped_column(nullable=False, default=0)
    score_status: Mapped[str] = mapped_column(String(50), nullable=False, default="CALCULATED", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
