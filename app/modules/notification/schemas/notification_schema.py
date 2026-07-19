from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationTemplateCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    channel: str
    subject_template: str | None = None
    body_template: str
    variables_json: list[str] = []
    is_active: bool = True


class NotificationPreferenceUpsert(BaseModel):
    channel: str
    is_enabled: bool = True
    quiet_hours_json: dict = {}
    config_json: dict = {}


class NotificationDispatchRecipientInput(BaseModel):
    user_id: str | None = None
    recipient_address: str | None = None
    channel: str


class NotificationDispatchCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    template_id: str | None = None
    source_module: str | None = None
    source_entity_type: str | None = None
    source_entity_id: str | None = None
    title: str
    message: str
    priority: str = "NORMAL"
    scheduled_at: datetime | None = None
    recipients: list[NotificationDispatchRecipientInput]


class NotificationTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    channel: str
    subject_template: str | None
    body_template: str
    variables_json: list[str]
    is_active: bool


class NotificationPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    user_id: UUID
    channel: str
    is_enabled: bool
    quiet_hours_json: dict
    config_json: dict


class NotificationRecipientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    notification_id: UUID
    user_id: UUID | None
    channel: str
    recipient_address: str | None
    delivery_status: str
    is_read: bool
    is_primary: bool
    read_at: datetime | None


class NotificationDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    notification_id: UUID
    recipient_id: UUID
    channel: str
    provider_name: str | None
    provider_message_id: str | None
    attempt_no: int
    status: str
    delivered_at: datetime | None
    failure_reason: str | None
    payload_json: dict
    response_json: dict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    template_id: UUID | None
    source_module: str | None
    source_entity_type: str | None
    source_entity_id: UUID | None
    title: str
    message: str
    priority: str
    status: str
    scheduled_at: datetime | None
    sent_at: datetime | None


class NotificationBundleRead(BaseModel):
    notification: NotificationRead
    recipients: list[NotificationRecipientRead]
    deliveries: list[NotificationDeliveryRead]


class InboxItemRead(BaseModel):
    recipient: NotificationRecipientRead
    notification: NotificationRead
