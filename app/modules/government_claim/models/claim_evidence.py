from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClaimEvidence(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "claim_evidences"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    claim_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("government_claims.id"), nullable=False, index=True)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False, default="SUPPORTING_DOCUMENT")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
