from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Float, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class CostPolicy(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "cost_policies"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_cost_policies_tenant_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    labor_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    utility_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    packaging_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    distribution_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    overhead_cost_per_portion: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    waste_cost_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
