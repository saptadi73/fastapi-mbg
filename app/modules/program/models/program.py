from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Program(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "programs"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    program_type: Mapped[str] = mapped_column(String(50), default="PUBLIC", nullable=False)
    funding_source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
