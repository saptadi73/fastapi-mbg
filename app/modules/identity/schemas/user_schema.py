from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CurrentUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    active_sppg_id: UUID | None
    full_name: str
    email: EmailStr
    role_names: list[str]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    active_sppg_id: UUID | None = None
