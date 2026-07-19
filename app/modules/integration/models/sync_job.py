from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SyncJob(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "sync_jobs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_system_id", "job_name", name="uq_sync_jobs_tenant_system_job"),
    )

    external_system_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_systems.id"),
        nullable=False,
        index=True,
    )
    job_name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False, default="OUTBOUND")
    trigger_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="MANUAL")
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="READY")
    schedule_expression: Mapped[str | None] = mapped_column(String(120), nullable=True)
    filter_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
