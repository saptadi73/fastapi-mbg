from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PurchaseRequestLine(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "purchase_request_lines"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    purchase_request_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requests.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    uom_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uoms.id"), nullable=False)
    requested_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    shortage_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    estimated_total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
