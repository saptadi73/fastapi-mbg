from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Vehicle(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "vehicle_code", name="uq_vehicles_tenant_vehicle_code"),
        UniqueConstraint("tenant_id", "plate_number", name="uq_vehicles_tenant_plate_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    home_sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    vehicle_type_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vehicle_types.id"), nullable=True, index=True)
    vehicle_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    plate_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ownership_status: Mapped[str] = mapped_column(String(50), nullable=False, default="OWNED")
    brand_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacture_year: Mapped[int | None] = mapped_column(nullable=True)
    capacity_portions: Mapped[int | None] = mapped_column(nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
