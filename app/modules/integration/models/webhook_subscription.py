from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WebhookSubscription(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "webhook_subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "external_system_id",
            "subscription_name",
            name="uq_webhook_subscriptions_tenant_system_name",
        ),
    )

    external_system_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_systems.id"),
        nullable=False,
        index=True,
    )
    subscription_name: Mapped[str] = mapped_column(String(120), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    endpoint_path: Mapped[str] = mapped_column(String(255), nullable=False)
    signing_secret_masked: Mapped[str | None] = mapped_column(String(255), nullable=True)
    headers_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
