from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProgramPeriod(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "program_periods"
    __table_args__ = (
        UniqueConstraint("program_id", "code", name="uq_program_periods_program_code"),
    )

    program_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_start: Mapped[date] = mapped_column(Date, nullable=False)
    date_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
