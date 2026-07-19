from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryProof(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "delivery_proofs"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    delivery_order_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_orders.id"),
        nullable=False,
        index=True,
    )
    route_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_routes.id"), nullable=True, index=True)
    route_stop_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_route_stops.id"),
        nullable=True,
        index=True,
    )
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(255), nullable=False)
    receiver_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    received_portions: Mapped[int] = mapped_column(Integer, nullable=False)
    rejected_portions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    temperature_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)
    condition_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condition_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    signature_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    signature_signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    incident_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linked_incident_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
