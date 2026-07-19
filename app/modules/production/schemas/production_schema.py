from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductionOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    meal_plan_id: UUID
    production_number: str
    production_date: date
    status: str
    planned_portions: int
    actual_portions: int | None
    accepted_portions: int | None
    rejected_portions: int | None
    started_at: datetime | None
    completed_at: datetime | None
    actual_total_cost: float
    actual_cost_per_portion: float


class ProductionMaterialConsumptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    production_order_id: UUID
    product_id: UUID
    warehouse_id: UUID
    planned_quantity: float
    actual_quantity: float
    uom_id: UUID
    unit_cost: float
    total_cost: float


class ProductionOrderComplete(BaseModel):
    actual_portions: int
    accepted_portions: int
    rejected_portions: int = 0


class ProductionOrderBundleRead(BaseModel):
    production_order: ProductionOrderRead
    materials: list[ProductionMaterialConsumptionRead]


class ProductionCostSheetRead(BaseModel):
    production_order_id: str
    planned_portions: int
    actual_portions: int | None
    accepted_portions: int | None
    rejected_portions: int | None
    total_actual_material_cost: float
    actual_cost_per_produced_portion: float
    actual_cost_per_accepted_portion: float
    materials: list[dict]
