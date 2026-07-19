from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class GovernmentClaimLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "government_claim_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    claim_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("government_claims.id"), nullable=False, index=True)
    delivery_order_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=True, index=True)
    production_order_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("production_orders.id"), nullable=True, index=True)
    line_type: Mapped[str] = mapped_column(String(50), nullable=False, default="DELIVERY_ACTUAL_COST")
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    portions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    line_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
