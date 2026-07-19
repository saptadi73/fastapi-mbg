from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryOrder(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "delivery_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "delivery_number", name="uq_delivery_orders_tenant_delivery_number"),
    )

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    production_order_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("production_orders.id"),
        nullable=False,
        index=True,
    )
    route_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_routes.id"),
        nullable=True,
        index=True,
    )
    school_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    delivery_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    planned_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_portions: Mapped[int] = mapped_column(Integer, nullable=False)
    shipped_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    received_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rejected_portions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLANNED")
    receiver_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_gps: Mapped[str | None] = mapped_column(String(120), nullable=True)
