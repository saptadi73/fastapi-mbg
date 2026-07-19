from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CostPolicyCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    code: str
    name: str
    effective_from: date
    effective_to: date | None = None
    labor_cost_per_portion: float = 0
    utility_cost_per_portion: float = 0
    packaging_cost_per_portion: float = 0
    distribution_cost_per_portion: float = 0
    overhead_cost_per_portion: float = 0
    waste_cost_percentage: float = 0
    is_active: bool = True


class CostPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    code: str
    name: str
    effective_from: date
    effective_to: date | None
    labor_cost_per_portion: float
    utility_cost_per_portion: float
    packaging_cost_per_portion: float
    distribution_cost_per_portion: float
    overhead_cost_per_portion: float
    waste_cost_percentage: float
    is_active: bool


class ProductionCostSummaryRead(BaseModel):
    production_order_id: str
    meal_plan_id: str
    tenant_id: str
    sppg_id: str
    applied_cost_policy_id: str | None
    labor_cost_source: str
    accepted_portions: int
    planned_portions: int
    actual_portions: int
    rejected_portions: int
    material_cost: float
    labor_cost: float
    utility_cost: float
    packaging_cost: float
    distribution_cost: float
    overhead_cost: float
    waste_cost: float
    total_actual_cost: float
    actual_cost_per_accepted_portion: float
    budget_cost_per_portion: float
    budget_total_for_accepted_portions: float
    variance_total: float
    variance_per_portion: float
    materials: list[dict]
