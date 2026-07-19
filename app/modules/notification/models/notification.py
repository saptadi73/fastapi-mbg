from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Notification(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    sppg_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sppg.id"),
        nullable=True,
        index=True,
    )
    template_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notification_templates.id"),
        nullable=True,
        index=True,
    )
    source_module: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source_entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_entity_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(4000), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="NORMAL", index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED", index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
