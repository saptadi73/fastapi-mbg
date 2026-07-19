from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class FeedbackItem(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "feedback_items"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    feedback_submission_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feedback_submissions.id"),
        nullable=False,
        index=True,
    )
    item_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float | None] = mapped_column(nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comment_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
