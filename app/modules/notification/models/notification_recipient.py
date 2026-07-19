from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationRecipient(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "notification_recipients"

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
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recipient_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
