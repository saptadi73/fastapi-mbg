from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class OutboundMessage(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "outbound_messages"
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_system_id", "idempotency_key", name="uq_outbound_messages_tenant_system_idempotency"),
    )

    external_system_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_systems.id"),
        nullable=False,
        index=True,
    )
    sync_job_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sync_jobs.id"), nullable=True, index=True)
    message_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="QUEUED")
    destination_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
