from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryRouteStop(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "delivery_route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "stop_sequence", name="uq_delivery_route_stops_route_sequence"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    route_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_routes.id"),
        nullable=False,
        index=True,
    )
    delivery_order_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_orders.id"),
        nullable=True,
        index=True,
    )
    school_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    stop_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLANNED")
    recipient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stop_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
