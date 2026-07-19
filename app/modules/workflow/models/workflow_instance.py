from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkflowInstance(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "workflow_instances"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "document_type",
            "document_id",
            name="uq_workflow_instances_tenant_document",
        ),
    )

    workflow_definition_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_definitions.id"),
        nullable=False,
        index=True,
    )
    workflow_version_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_versions.id"),
        nullable=True,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    current_state: Mapped[str] = mapped_column(String(50), nullable=False)
    last_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
