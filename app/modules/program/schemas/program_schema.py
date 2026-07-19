from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgramCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    program_type: str = "PUBLIC"
    funding_source_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "DRAFT"
    is_active: bool = True


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    program_type: str
    funding_source_name: str | None
    start_date: date | None
    end_date: date | None
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProgramPeriodCreate(BaseModel):
    code: str
    name: str
    date_start: date
    date_end: date
    status: str = "DRAFT"
    notes: str | None = None


class ProgramPeriodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    code: str
    name: str
    date_start: date
    date_end: date
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ProgramTenantAssignmentCreate(BaseModel):
    tenant_id: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True
    notes: str | None = None


class ProgramTenantAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    tenant_id: UUID
    start_date: date | None
    end_date: date | None
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ProgramSppgAssignmentCreate(BaseModel):
    tenant_id: str | None = None
    sppg_id: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True
    notes: str | None = None


class ProgramSppgAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    tenant_id: UUID
    sppg_id: UUID
    start_date: date | None
    end_date: date | None
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ProgramBundleRead(BaseModel):
    program: ProgramRead
    periods: list[ProgramPeriodRead]
    tenant_assignments: list[ProgramTenantAssignmentRead]
    sppg_assignments: list[ProgramSppgAssignmentRead]
