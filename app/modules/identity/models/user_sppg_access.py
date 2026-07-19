from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UserSppgAccess(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_sppg_access"
    __table_args__ = (
        UniqueConstraint("user_id", "sppg_id", name="uq_user_sppg_access_user_sppg"),
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    sppg_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sppg.id"),
        nullable=False,
        index=True,
    )
