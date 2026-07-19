from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentLink(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "document_links"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "linked_entity_type",
            "linked_entity_id",
            name="uq_document_links_document_entity",
        ),
    )

    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    linked_entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    linked_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ATTACHMENT")
