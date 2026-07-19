from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkflowState(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "workflow_states"
    __table_args__ = (
        UniqueConstraint("workflow_version_id", "state_code", name="uq_workflow_states_version_code"),
    )

    workflow_version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_versions.id"),
        nullable=False,
        index=True,
    )
    state_code: Mapped[str] = mapped_column(String(50), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_initial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sla_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
