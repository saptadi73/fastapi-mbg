from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryIncident(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "delivery_incidents"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    delivery_order_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_orders.id"),
        nullable=True,
        index=True,
    )
    route_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_routes.id"),
        nullable=True,
        index=True,
    )
    route_stop_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_route_stops.id"),
        nullable=True,
        index=True,
    )
    incident_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    incident_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)
    media_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    resolution_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
