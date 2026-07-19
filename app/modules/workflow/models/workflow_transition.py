from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkflowTransition(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "workflow_transitions"
    __table_args__ = (
        UniqueConstraint(
            "workflow_definition_id",
            "from_state",
            "action_name",
            name="uq_workflow_transitions_definition_state_action",
        ),
    )

    workflow_definition_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_definitions.id"),
        nullable=False,
        index=True,
    )
    from_state: Mapped[str] = mapped_column(String(50), nullable=False)
    action_name: Mapped[str] = mapped_column(String(50), nullable=False)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    allowed_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
