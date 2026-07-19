from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MonthlyBudgetRealizationSummary(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "monthly_budget_realization_summaries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "period_month", name="uq_monthly_budget_realization_tenant_month"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    period_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    budgets_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    effective_budget: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    reserved_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    committed_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    actual_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    refresh_source: Mapped[str] = mapped_column(String(50), nullable=False, default="SUMMARY_TABLE")
