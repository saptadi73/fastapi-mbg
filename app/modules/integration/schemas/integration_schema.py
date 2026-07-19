from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    config_json: dict = Field(default_factory=dict)
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
    payload_json: dict = Field(default_factory=dict)
    response_json: dict = Field(default_factory=dict)
    processed_at: datetime | None = None
    notes: str | None = None


class WebhookSubscriptionCreate(BaseModel):
    external_system_id: str
    subscription_name: str
    event_type: str
    endpoint_path: str
    signing_secret_masked: str | None = None
    headers_json: dict = Field(default_factory=dict)
    is_active: bool = True
    notes: str | None = None


class DataMappingCreate(BaseModel):
    external_system_id: str
    mapping_name: str
    source_entity: str
    target_entity: str
    direction: str = "BIDIRECTIONAL"
    mapping_config_json: dict = Field(default_factory=dict)
    is_active: bool = True
    notes: str | None = None


class SyncJobCreate(BaseModel):
    external_system_id: str
    job_name: str
    direction: str = "OUTBOUND"
    trigger_mode: str = "MANUAL"
    entity_type: str
    schedule_expression: str | None = None
    filter_json: dict = Field(default_factory=dict)
    next_run_at: datetime | None = None
    notes: str | None = None


class InboundMessageCreate(BaseModel):
    external_system_id: str
    webhook_subscription_id: str | None = None
    message_type: str
    external_reference: str | None = None
    idempotency_key: str
    status: str = "RECEIVED"
    headers_json: dict = Field(default_factory=dict)
    payload_json: dict = Field(default_factory=dict)
    received_at: datetime
    processed_at: datetime | None = None
    notes: str | None = None


class WebhookReceiveCreate(BaseModel):
    message_type: str
    external_reference: str | None = None
    idempotency_key: str
    headers_json: dict = Field(default_factory=dict)
    payload_json: dict = Field(default_factory=dict)
    received_at: datetime | None = None
    notes: str | None = None


class OutboundMessageCreate(BaseModel):
    external_system_id: str
    sync_job_id: str | None = None
    message_type: str
    entity_type: str | None = None
    entity_id: str | None = None
    external_reference: str | None = None
    idempotency_key: str
    status: str = "QUEUED"
    destination_url: str | None = None
    payload_json: dict = Field(default_factory=dict)
    response_json: dict = Field(default_factory=dict)
    retry_count: int = 0
    queued_at: datetime
    processed_at: datetime | None = None
    notes: str | None = None


class SyncJobRunCreate(BaseModel):
    message_type: str
    external_reference: str | None = None
    idempotency_key: str
    entity_id: str | None = None
    destination_url: str | None = None
    payload_json: dict = Field(default_factory=dict)
    response_json: dict = Field(default_factory=dict)
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


class WebhookSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    subscription_name: str
    event_type: str
    endpoint_path: str
    signing_secret_masked: str | None
    headers_json: dict
    is_active: bool
    last_received_at: datetime | None
    notes: str | None


class DataMappingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    mapping_name: str
    source_entity: str
    target_entity: str
    direction: str
    mapping_config_json: dict
    is_active: bool
    notes: str | None


class SyncJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    job_name: str
    direction: str
    trigger_mode: str
    entity_type: str
    status: str
    schedule_expression: str | None
    filter_json: dict
    last_run_at: datetime | None
    last_success_at: datetime | None
    next_run_at: datetime | None
    notes: str | None


class InboundMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    webhook_subscription_id: UUID | None
    message_type: str
    external_reference: str | None
    idempotency_key: str
    status: str
    headers_json: dict
    payload_json: dict
    received_at: datetime
    processed_at: datetime | None
    notes: str | None


class OutboundMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    external_system_id: UUID
    sync_job_id: UUID | None
    message_type: str
    entity_type: str | None
    entity_id: UUID | None
    external_reference: str | None
    idempotency_key: str
    status: str
    destination_url: str | None
    payload_json: dict
    response_json: dict
    retry_count: int
    queued_at: datetime
    processed_at: datetime | None
    notes: str | None


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
    webhook_subscriptions: list[WebhookSubscriptionRead] = Field(default_factory=list)
    data_mappings: list[DataMappingRead] = Field(default_factory=list)
    sync_jobs: list[SyncJobRead] = Field(default_factory=list)
