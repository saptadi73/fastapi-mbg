from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationDelivery(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "notification_deliveries"

    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    notification_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notification_recipients.id"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    response_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
