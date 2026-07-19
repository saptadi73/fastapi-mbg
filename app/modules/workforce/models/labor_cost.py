from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class LaborCost(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "labor_costs"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    timesheet_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("timesheets.id"), nullable=True, index=True)
    cost_date: Mapped[date] = mapped_column(Date, nullable=False)
    cost_component: Mapped[str] = mapped_column(String(100), nullable=False, default="LABOR")
    hours_worked: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
