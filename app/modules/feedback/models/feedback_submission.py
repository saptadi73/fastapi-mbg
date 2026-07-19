from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.core.database.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class FeedbackSubmission(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "feedback_submissions"

    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    sppg_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sppg.id"), nullable=False, index=True)
    school_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True, index=True)
    meal_plan_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_plans.id"), nullable=True, index=True)
    delivery_order_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=True, index=True)
    feedback_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    respondent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    respondent_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    overall_rating: Mapped[float | None] = mapped_column(nullable=True)
    acceptance_rate: Mapped[float | None] = mapped_column(nullable=True)
    food_waste_portions: Mapped[float | None] = mapped_column(nullable=True)
    delivery_timeliness_rating: Mapped[float | None] = mapped_column(nullable=True)
    temperature_rating: Mapped[float | None] = mapped_column(nullable=True)
    comment_text: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SUBMITTED", index=True)
