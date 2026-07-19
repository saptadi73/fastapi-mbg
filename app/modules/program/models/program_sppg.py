from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProgramSppg(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "program_sppg"
    __table_args__ = (
        UniqueConstraint("program_id", "sppg_id", name="uq_program_sppg_program_sppg"),
    )

    program_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
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
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
