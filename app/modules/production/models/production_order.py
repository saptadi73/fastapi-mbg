from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ProductionOrder(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "production_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "production_number", name="uq_production_orders_tenant_production_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    meal_plan_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_plans.id"), nullable=False, index=True)
    production_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLANNED")
    planned_portions: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accepted_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rejected_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    actual_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
