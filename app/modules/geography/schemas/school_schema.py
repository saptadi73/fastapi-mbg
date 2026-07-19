from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SchoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    school_level: str
    address: str
    latitude: float
    longitude: float
    student_count: int
    active_beneficiary_count: int


class SchoolCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    school_level: str
    address: str
    latitude: float
    longitude: float
    student_count: int = 0
