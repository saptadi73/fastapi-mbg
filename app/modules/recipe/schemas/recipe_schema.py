from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    product_id: UUID
    code: str
    name: str
    version: int
    output_quantity: float
    output_uom_id: UUID
    effective_from: date
    status: str
    is_active: bool


class RecipeCreate(BaseModel):
    tenant_id: str
    product_id: str
    code: str
    name: str
    version: int = 1
    output_quantity: float
    output_uom_id: str
    effective_from: date
    status: str = "DRAFT"
    is_active: bool = True


class RecipeLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    recipe_id: UUID
    component_product_id: UUID
    quantity: float
    uom_id: UUID
    waste_percentage: float
    sequence: int


class RecipeLineCreate(BaseModel):
    tenant_id: str
    component_product_id: str
    quantity: float
    uom_id: str
    waste_percentage: float = 0
    sequence: int = 1
