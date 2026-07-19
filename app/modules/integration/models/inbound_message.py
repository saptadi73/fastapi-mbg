from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class InboundMessage(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "inbound_messages"
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_system_id", "idempotency_key", name="uq_inbound_messages_tenant_system_idempotency"),
    )

    external_system_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_systems.id"),
        nullable=False,
        index=True,
    )
    webhook_subscription_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhook_subscriptions.id"),
        nullable=True,
        index=True,
    )
    message_type: Mapped[str] = mapped_column(String(120), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="RECEIVED")
    headers_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
