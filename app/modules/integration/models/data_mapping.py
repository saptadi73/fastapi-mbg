from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DataMapping(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "data_mappings"
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_system_id", "mapping_name", name="uq_data_mappings_tenant_system_name"),
    )

    external_system_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_systems.id"),
        nullable=False,
        index=True,
    )
    mapping_name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_entity: Mapped[str] = mapped_column(String(120), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False, default="BIDIRECTIONAL")
    mapping_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
