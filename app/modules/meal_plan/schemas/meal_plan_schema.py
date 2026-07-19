from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MealPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    recipe_id: UUID
    plan_date: date
    meal_type: str
    status: str
    planned_portions: int
    budget_cost_per_portion: float
    notes: str | None


class MealPlanCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    recipe_id: str
    plan_date: date
    meal_type: str
    status: str = "DRAFT"
    planned_portions: int
    budget_cost_per_portion: float = 0
    notes: str | None = None


class MealPlanStatusTransitionRead(BaseModel):
    id: UUID
    status: str


class MealPlanMaterialReservationRead(BaseModel):
    meal_plan_id: str
    status: str
    reserved_items: list[dict]


class MealPlanCostPreviewRead(BaseModel):
    meal_plan_id: str
    planned_portions: int
    currency: str
    cost_per_portion: float
    total_estimated_cost: float
    line_items: list[dict]
