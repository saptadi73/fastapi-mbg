from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExternalSystemCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    system_type: str
    base_url: str | None = None
    is_active: bool = True
    notes: str | None = None


class IntegrationCredentialCreate(BaseModel):
    credential_name: str
    credential_type: str = "API_KEY"
    secret_masked: str | None = None
    config_json: dict = {}
    is_active: bool = True


class SyncLogCreate(BaseModel):
    external_system_id: str
    direction: str = "OUTBOUND"
    message_type: str
    entity_type: str | None = None
    entity_id: str | None = None
    external_reference: str | None = None
    idempotency_key: str
    status: str = "PENDING"
    payload_json: dict = {}
    response_json: dict = {}
    processed_at: datetime | None = None
    notes: str | None = None


class ExternalSystemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    system_type: str
    base_url: str | None
    is_active: bool
    notes: str | None


class IntegrationCredentialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    credential_name: str
    credential_type: str
    secret_masked: str | None
    config_json: dict
    is_active: bool


class SyncLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    direction: str
    message_type: str
    entity_type: str | None
    entity_id: UUID | None
    external_reference: str | None
    idempotency_key: str
    status: str
    payload_json: dict
    response_json: dict
    processed_at: datetime | None
    notes: str | None


class ExternalSystemBundleRead(BaseModel):
    external_system: ExternalSystemRead
    credentials: list[IntegrationCredentialRead]
