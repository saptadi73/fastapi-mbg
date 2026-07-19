from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class WorkflowVersionCreate(BaseModel):
    status: str = "DRAFT"
    is_active: bool = True
    notes: str | None = None


class WorkflowStateCreate(BaseModel):
    state_code: str
    state_name: str
    sequence_number: int = 1
    is_initial: bool = False
    is_terminal: bool = False
    sla_hours: int | None = None


class WorkflowActionCreate(BaseModel):
    action_code: str
    action_name: str
    allowed_role: str | None = None
    requires_approval: bool = False
    is_active: bool = True


class ApprovalRequestCreate(BaseModel):
    notes: str | None = None
    due_at: datetime | None = None


class ApprovalDecisionCreate(BaseModel):
    decision: str
    notes: str | None = None


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


class WorkflowVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_definition_id: UUID
    version_number: int
    status: str
    is_active: bool
    notes: str | None


class WorkflowStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_version_id: UUID
    state_code: str
    state_name: str
    sequence_number: int
    is_initial: bool
    is_terminal: bool
    sla_hours: int | None


class WorkflowActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_version_id: UUID
    action_code: str
    action_name: str
    allowed_role: str | None
    requires_approval: bool
    is_active: bool


class WorkflowInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_definition_id: UUID
    workflow_version_id: UUID | None
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
    approval_request_id: UUID | None
    created_at: datetime


class ApprovalRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    workflow_instance_id: UUID
    requested_state: str
    requested_action: str
    requested_by_user_id: UUID | None
    requested_by_name: str | None
    status: str
    due_at: datetime | None
    notes: str | None


class ApprovalDecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    approval_request_id: UUID
    decision: str
    decision_by_user_id: UUID | None
    decision_by_name: str | None
    decision_at: datetime
    notes: str | None


class WorkflowBundleRead(BaseModel):
    definition: WorkflowDefinitionRead
    versions: list[WorkflowVersionRead] = Field(default_factory=list)
    states: list[WorkflowStateRead] = Field(default_factory=list)
    actions: list[WorkflowActionRead] = Field(default_factory=list)
    transitions: list[WorkflowTransitionRead]


class WorkflowInstanceBundleRead(BaseModel):
    definition: WorkflowDefinitionRead
    instance: WorkflowInstanceRead
    version: WorkflowVersionRead | None = None
    states: list[WorkflowStateRead] = Field(default_factory=list)
    actions: list[WorkflowActionRead] = Field(default_factory=list)
    transitions: list[WorkflowTransitionRead]
    history: list[WorkflowHistoryRead]
    approval_requests: list[ApprovalRequestRead] = Field(default_factory=list)
    approval_decisions: list[ApprovalDecisionRead] = Field(default_factory=list)
