from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetCategoryCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    asset_account_id: str | None = None
    depreciation_expense_account_id: str | None = None
    accumulated_depreciation_account_id: str | None = None
    useful_life_months: int | None = None
    depreciation_method: str = "STRAIGHT_LINE"
    is_active: bool = True


class AssetCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    asset_category_id: str | None = None
    asset_code: str
    asset_name: str
    acquisition_date: date
    acquisition_cost: float
    residual_value: float = 0
    useful_life_months: int | None = None
    depreciation_method: str = "STRAIGHT_LINE"
    status: str = "ACTIVE"
    serial_number: str | None = None
    condition_status: str | None = None
    location_name: str | None = None
    is_active: bool = True
    notes: str | None = None


class AssetAssignmentCreate(BaseModel):
    sppg_id: str
    assigned_to_name: str | None = None
    assignment_date: date
    end_date: date | None = None
    assignment_role: str = "OPERATIONAL"
    status: str = "ASSIGNED"
    is_active: bool = True
    notes: str | None = None


class AssetDepreciationCreate(BaseModel):
    depreciation_date: date
    depreciation_amount: float | None = None
    debit_account_code: str | None = None
    credit_account_code: str | None = None
    status: str = "POSTED"
    notes: str | None = None


class AssetCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    asset_account_id: UUID | None
    depreciation_expense_account_id: UUID | None
    accumulated_depreciation_account_id: UUID | None
    useful_life_months: int | None
    depreciation_method: str
    is_active: bool


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    asset_category_id: UUID | None
    asset_code: str
    asset_name: str
    acquisition_date: date
    acquisition_cost: float
    residual_value: float
    useful_life_months: int | None
    depreciation_method: str
    status: str
    serial_number: str | None
    condition_status: str | None
    location_name: str | None
    is_active: bool
    notes: str | None


class AssetAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    asset_id: UUID
    assigned_to_name: str | None
    assignment_date: date
    end_date: date | None
    assignment_role: str
    status: str
    is_active: bool
    notes: str | None


class AssetDepreciationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    asset_id: UUID
    journal_entry_id: UUID | None
    depreciation_date: date
    depreciation_amount: float
    accumulated_depreciation_amount: float
    book_value_after: float
    status: str
    notes: str | None


class AssetBundleRead(BaseModel):
    asset: AssetRead
    assignments: list[AssetAssignmentRead]
    depreciations: list[AssetDepreciationRead]
