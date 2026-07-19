from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ApprovalDecision(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "approval_decisions"

    approval_request_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("approval_requests.id"),
        nullable=False,
        index=True,
    )
    decision: Mapped[str] = mapped_column(String(30), nullable=False)
    decision_by_user_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decision_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
