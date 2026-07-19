from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BeneficiaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    school_id: UUID
    external_reference: str
    category: str
    age_group: str
    gender: str | None
    dietary_restriction: str | None
    allergy_notes: str | None
    is_active: bool


class BeneficiaryCreate(BaseModel):
    tenant_id: str
    school_id: str
    external_reference: str
    category: str
    age_group: str
    gender: str | None = None
    dietary_restriction: str | None = None
    allergy_notes: str | None = None
    is_active: bool = True
