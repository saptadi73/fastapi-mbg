from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CurrentUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    active_sppg_id: UUID | None
    accessible_sppg_ids: list[UUID]
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
    accessible_sppg_ids: list[UUID] = []


class UserSppgAccessRead(BaseModel):
    user_id: UUID
    tenant_id: UUID
    active_sppg_id: UUID | None
    accessible_sppg_ids: list[UUID]


class UserSppgAccessUpdate(BaseModel):
    accessible_sppg_ids: list[str]
    active_sppg_id: str | None = None


class UserAdminRead(BaseModel):
    id: UUID
    tenant_id: UUID
    active_sppg_id: UUID | None
    accessible_sppg_ids: list[UUID]
    full_name: str
    email: EmailStr
    role_names: list[str]
    is_active: bool


class UserCreate(BaseModel):
    tenant_id: str
    full_name: str
    email: EmailStr
    password: str
    role_names: list[str]
    is_active: bool = True
    accessible_sppg_ids: list[str] = []
    active_sppg_id: str | None = None


class UserUpdate(BaseModel):
    full_name: str
    role_names: list[str]
    is_active: bool = True
    password: str | None = None
    accessible_sppg_ids: list[str] = []
    active_sppg_id: str | None = None


class ActiveSppgSwitchRequest(BaseModel):
    sppg_id: str
