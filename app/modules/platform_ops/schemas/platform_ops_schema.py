from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BackgroundJobCreate(BaseModel):
    tenant_id: str
    job_name: str
    job_type: str
    payload_json: dict = Field(default_factory=dict)
    scheduled_at: datetime | None = None
    notes: str | None = None


class BackgroundJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    job_name: str
    job_type: str
    status: str
    payload_json: dict
    result_json: dict
    scheduled_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    notes: str | None


class OutboxEventCreate(BaseModel):
    tenant_id: str
    event_name: str
    aggregate_type: str
    aggregate_id: str | None = None
    payload_json: dict = Field(default_factory=dict)
    available_at: datetime | None = None


class OutboxEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    event_name: str
    aggregate_type: str
    aggregate_id: UUID | None
    status: str
    payload_json: dict
    available_at: datetime
    processed_at: datetime | None
    retry_count: int
    last_error: str | None


class DailyKitchenOperationSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    summary_date: date
    meal_plan_count: int
    production_order_count: int
    delivery_order_count: int
    accepted_portions: int
    delivered_portions: int
    rejected_portions: int
    labor_cost_amount: float
    refresh_source: str


class MonthlyBudgetRealizationSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    period_month: date
    budgets_count: int
    effective_budget: float
    reserved_amount: float
    committed_amount: float
    actual_amount: float
    refresh_source: str


class SummaryRefreshRequest(BaseModel):
    summary_date: date | None = None
    period_month: date | None = None


class MaterializedViewRefreshRead(BaseModel):
    view_name: str
    refreshed: bool
    row_count: int
