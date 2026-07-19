from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class BudgetLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "budget_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    budget_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    planned_amount: Mapped[float] = mapped_column(Float, nullable=False)
    revised_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    control_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="WARNING")
    tolerance_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cached_reserved_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cached_committed_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cached_actual_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
