from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DailyKitchenOperationSummary(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "daily_kitchen_operation_summaries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sppg_id", "summary_date", name="uq_daily_kitchen_operation_scope_date"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_plan_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    production_order_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivery_order_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_portions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_portions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_portions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    labor_cost_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    refresh_source: Mapped[str] = mapped_column(String(50), nullable=False, default="SUMMARY_TABLE")
