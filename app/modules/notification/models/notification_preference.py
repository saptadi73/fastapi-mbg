from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationPreference(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", "channel", name="uq_notification_preferences_tenant_user_channel"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quiet_hours_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
