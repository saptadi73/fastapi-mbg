from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class VehicleLocation(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "vehicle_locations"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=True, index=True)
    vehicle_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    assignment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_assignments.id"),
        nullable=True,
        index=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    location: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
    )
    speed_kph: Mapped[float | None] = mapped_column(nullable=True)
    heading_degree: Mapped[float | None] = mapped_column(nullable=True)
    accuracy_meter: Mapped[float | None] = mapped_column(nullable=True)
    engine_on: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    movement_status: Mapped[str] = mapped_column(String(50), nullable=False, default="IDLE", index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PING", index=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
