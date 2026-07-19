from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QCInspectionCreate(BaseModel):
    tenant_id: str
    sppg_id: str
    inspection_type: str = "PRODUCTION"
    stage: str = "PRODUCTION_OUTPUT"
    reference_type: str
    reference_id: str
    inspection_at: datetime
    inspector_name: str
    is_mandatory_for_release: bool = True
    notes: str | None = None


class QCInspectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    inspection_number: str
    inspection_type: str
    stage: str
    reference_type: str
    reference_id: UUID
    inspection_at: datetime
    inspector_name: str
    status: str
    overall_result: str | None
    is_mandatory_for_release: bool
    notes: str | None


class QCInspectionLineCreate(BaseModel):
    parameter_name: str
    expected_value: str | None = None
    actual_value: str | None = None
    result_status: str = "PASS"
    notes: str | None = None


class QCInspectionLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    inspection_id: UUID
    parameter_name: str
    expected_value: str | None
    actual_value: str | None
    result_status: str
    notes: str | None


class QCInspectionBundleRead(BaseModel):
    inspection: QCInspectionRead
    lines: list[QCInspectionLineRead]
