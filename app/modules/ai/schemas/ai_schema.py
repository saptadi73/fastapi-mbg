from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIForecastCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    forecast_type: str
    forecast_date: date
    target_date: date
    model_name: str | None = None
    input_snapshot: dict = Field(default_factory=dict)
    forecast_payload: dict = Field(default_factory=dict)
    confidence_score: float | None = None
    status: str = "GENERATED"
    notes: str | None = None


class AIRecommendationCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    recommendation_date: date
    recommendation_type: str
    reference_type: str | None = None
    reference_id: str | None = None
    title: str
    summary_text: str
    recommendation_payload: dict = Field(default_factory=dict)
    priority: str = "MEDIUM"
    status: str = "OPEN"
    notes: str | None = None


class AIDailySummaryCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    summary_date: date
    summary_type: str = "OPERATIONS"
    headline: str
    summary_text: str
    metrics_payload: dict = Field(default_factory=dict)
    anomaly_count: int = 0
    recommendation_count: int = 0
    status: str = "GENERATED"
    notes: str | None = None


class AIForecastRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    forecast_type: str
    forecast_date: date
    target_date: date
    model_name: str | None
    input_snapshot: dict
    forecast_payload: dict
    confidence_score: float | None
    status: str
    notes: str | None


class AIRecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    recommendation_date: date
    recommendation_type: str
    reference_type: str | None
    reference_id: UUID | None
    title: str
    summary_text: str
    recommendation_payload: dict
    priority: str
    status: str
    notes: str | None


class AIDailySummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    summary_date: date
    summary_type: str
    headline: str
    summary_text: str
    metrics_payload: dict
    anomaly_count: int
    recommendation_count: int
    status: str
    notes: str | None


class AIOverviewRead(BaseModel):
    totals: dict
    breakdown: dict
