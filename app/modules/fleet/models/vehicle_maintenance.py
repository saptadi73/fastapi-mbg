from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class VehicleMaintenance(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "vehicle_maintenances"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    vehicle_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    odometer_km: Mapped[float | None] = mapped_column(nullable=True)
    cost_amount: Mapped[float | None] = mapped_column(nullable=True)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED", index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
