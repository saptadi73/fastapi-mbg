from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BudgetLineCreate(BaseModel):
    category_name: str
    account_id: str | None = None
    planned_amount: float = Field(gt=0)
    revised_amount: float | None = None
    control_mode: str = "WARNING"
    tolerance_percentage: float = 0
    notes: str | None = None


class BudgetCreate(BaseModel):
    tenant_id: str
    name: str
    date_start: date
    date_end: date
    version_number: int = 1
    notes: str | None = None
    lines: list[BudgetLineCreate]


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    budget_number: str
    name: str
    date_start: date
    date_end: date
    version_number: int
    status: str
    approved_by: UUID | None
    approved_at: datetime | None
    notes: str | None


class BudgetLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    budget_id: UUID
    category_name: str
    account_id: UUID | None
    planned_amount: float
    revised_amount: float | None
    control_mode: str
    tolerance_percentage: float
    cached_reserved_amount: float
    cached_committed_amount: float
    cached_actual_amount: float
    notes: str | None


class BudgetBundleRead(BaseModel):
    budget: BudgetRead
    lines: list[BudgetLineRead]


class BudgetAvailabilityRead(BaseModel):
    budget_id: str
    totals: dict
    lines: list[dict]
