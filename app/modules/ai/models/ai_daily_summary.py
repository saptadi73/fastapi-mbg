from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIDailySummary(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "ai_daily_summaries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sppg_id", "summary_date", name="uq_ai_daily_summary_scope_date"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    summary_type: Mapped[str] = mapped_column(String(100), nullable=False, default="OPERATIONS", index=True)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    summary_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    metrics_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    anomaly_count: Mapped[int] = mapped_column(nullable=False, default=0)
    recommendation_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
