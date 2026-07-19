from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackItemCreate(BaseModel):
    item_type: str
    metric_name: str
    score: float | None = None
    sentiment: str | None = None
    comment_text: str | None = None


class FeedbackSubmissionCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    school_id: str | None = None
    meal_plan_id: str | None = None
    delivery_order_id: str | None = None
    feedback_date: date
    source_type: str
    respondent_name: str | None = None
    respondent_role: str | None = None
    overall_rating: float | None = None
    acceptance_rate: float | None = None
    food_waste_portions: float | None = None
    delivery_timeliness_rating: float | None = None
    temperature_rating: float | None = None
    comment_text: str | None = None
    status: str = "SUBMITTED"
    items: list[FeedbackItemCreate] = Field(default_factory=list)


class ComplaintCreate(BaseModel):
    feedback_submission_id: str | None = None
    complaint_date: datetime
    category: str
    severity: str = "MEDIUM"
    complaint_text: str
    resolution_status: str = "OPEN"
    resolved_at: datetime | None = None
    notes: str | None = None


class ServiceQualityScoreCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    score_date: date
    acceptance_score: float | None = None
    waste_score: float | None = None
    delivery_score: float | None = None
    temperature_score: float | None = None
    taste_score: float | None = None
    nutrition_score: float | None = None
    complaint_score: float | None = None
    total_score: float | None = None
    score_status: str = "CALCULATED"
    notes: str | None = None


class FeedbackItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    feedback_submission_id: UUID
    item_type: str
    metric_name: str
    score: float | None
    sentiment: str | None
    comment_text: str | None


class FeedbackSubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    school_id: UUID | None
    meal_plan_id: UUID | None
    delivery_order_id: UUID | None
    feedback_date: date
    source_type: str
    respondent_name: str | None
    respondent_role: str | None
    overall_rating: float | None
    acceptance_rate: float | None
    food_waste_portions: float | None
    delivery_timeliness_rating: float | None
    temperature_rating: float | None
    comment_text: str | None
    status: str


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    feedback_submission_id: UUID | None
    complaint_date: datetime
    category: str
    severity: str
    complaint_text: str
    resolution_status: str
    resolved_at: datetime | None
    notes: str | None


class ServiceQualityScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    score_date: date
    acceptance_score: float | None
    waste_score: float | None
    delivery_score: float | None
    temperature_score: float | None
    taste_score: float | None
    nutrition_score: float | None
    complaint_score: float | None
    total_score: float
    score_status: str
    notes: str | None


class FeedbackSubmissionBundleRead(BaseModel):
    submission: FeedbackSubmissionRead
    items: list[FeedbackItemRead]
    complaints: list[ComplaintRead]


class FeedbackSummaryRead(BaseModel):
    totals: dict
    averages: dict
    complaints: dict
