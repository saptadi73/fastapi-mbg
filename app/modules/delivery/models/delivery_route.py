from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryRoute(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "delivery_routes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "route_code", name="uq_delivery_routes_tenant_route_code"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    route_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    route_name: Mapped[str] = mapped_column(String(255), nullable=False)
    route_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLANNED")
    planned_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    origin_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    destination_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    total_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
