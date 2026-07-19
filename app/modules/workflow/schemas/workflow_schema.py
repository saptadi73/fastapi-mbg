from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowDefinitionCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    document_type: str
    initial_state: str = "DRAFT"
    is_active: bool = True


class WorkflowDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    document_type: str
    initial_state: str
    is_active: bool


class WorkflowTransitionCreate(BaseModel):
    from_state: str
    action_name: str
    to_state: str
    allowed_role: str | None = None
    requires_approval: bool = False


class WorkflowTransitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_definition_id: UUID
    from_state: str
    action_name: str
    to_state: str
    allowed_role: str | None
    requires_approval: bool


class WorkflowInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_definition_id: UUID
    document_type: str
    document_id: UUID
    current_state: str
    last_action: str | None


class WorkflowHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_instance_id: UUID
    from_state: str | None
    action_name: str
    to_state: str
    actor_user_id: UUID | None
    actor_name: str | None
    notes: str | None
    created_at: datetime


class WorkflowBundleRead(BaseModel):
    definition: WorkflowDefinitionRead
    transitions: list[WorkflowTransitionRead]


class WorkflowInstanceBundleRead(BaseModel):
    definition: WorkflowDefinitionRead
    instance: WorkflowInstanceRead
    transitions: list[WorkflowTransitionRead]
    history: list[WorkflowHistoryRead]
