from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    sppg_id: UUID | None
    actor_user_id: UUID | None
    actor_name: str | None
    event_type: str
    module_name: str
    action_name: str
    entity_type: str | None
    entity_id: UUID | None
    request_id: str | None
    success: bool
    ip_address: str | None
    summary: str
    metadata_json: dict
    occurred_at: datetime
