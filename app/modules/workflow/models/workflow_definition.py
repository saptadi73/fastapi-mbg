from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkflowDefinition(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "document_type", "code", name="uq_workflow_definitions_tenant_document_code"),
    )

    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    initial_state: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
