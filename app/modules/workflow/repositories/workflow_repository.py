from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workflow.models.approval_decision import ApprovalDecision
from app.modules.workflow.models.approval_request import ApprovalRequest
from app.modules.workflow.models.workflow_action import WorkflowAction
from app.modules.workflow.models.workflow_definition import WorkflowDefinition
from app.modules.workflow.models.workflow_history import WorkflowHistory
from app.modules.workflow.models.workflow_instance import WorkflowInstance
from app.modules.workflow.models.workflow_state import WorkflowState
from app.modules.workflow.models.workflow_transition import WorkflowTransition
from app.modules.workflow.models.workflow_version import WorkflowVersion


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_definitions(self, tenant_id: UUID | None = None) -> list[WorkflowDefinition]:
        query = select(WorkflowDefinition).order_by(WorkflowDefinition.document_type, WorkflowDefinition.name)
        if tenant_id is not None:
            query = query.where(WorkflowDefinition.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_definition_by_id(self, definition_id: UUID) -> WorkflowDefinition | None:
        return await self.session.get(WorkflowDefinition, definition_id)

    async def get_definition_by_document_type(self, tenant_id: UUID, document_type: str) -> WorkflowDefinition | None:
        result = await self.session.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.tenant_id == tenant_id,
                WorkflowDefinition.document_type == document_type,
                WorkflowDefinition.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def add_definition(self, definition: WorkflowDefinition) -> WorkflowDefinition:
        self.session.add(definition)
        await self.session.flush()
        await self.session.refresh(definition)
        return definition

    async def list_versions(self, workflow_definition_id: UUID) -> list[WorkflowVersion]:
        result = await self.session.execute(
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_definition_id == workflow_definition_id)
            .order_by(WorkflowVersion.version_number)
        )
        return list(result.scalars().all())

    async def get_version_by_id(self, version_id: UUID) -> WorkflowVersion | None:
        return await self.session.get(WorkflowVersion, version_id)

    async def get_active_version(self, workflow_definition_id: UUID) -> WorkflowVersion | None:
        result = await self.session.execute(
            select(WorkflowVersion)
            .where(
                WorkflowVersion.workflow_definition_id == workflow_definition_id,
                WorkflowVersion.is_active.is_(True),
            )
            .order_by(WorkflowVersion.version_number.desc())
        )
        return result.scalar_one_or_none()

    async def get_version_by_number(self, workflow_definition_id: UUID, version_number: int) -> WorkflowVersion | None:
        result = await self.session.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_definition_id == workflow_definition_id,
                WorkflowVersion.version_number == version_number,
            )
        )
        return result.scalar_one_or_none()

    async def add_version(self, version: WorkflowVersion) -> WorkflowVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def list_states(self, workflow_version_id: UUID) -> list[WorkflowState]:
        result = await self.session.execute(
            select(WorkflowState)
            .where(WorkflowState.workflow_version_id == workflow_version_id)
            .order_by(WorkflowState.sequence_number, WorkflowState.state_code)
        )
        return list(result.scalars().all())

    async def get_state(self, workflow_version_id: UUID, state_code: str) -> WorkflowState | None:
        result = await self.session.execute(
            select(WorkflowState).where(
                WorkflowState.workflow_version_id == workflow_version_id,
                WorkflowState.state_code == state_code,
            )
        )
        return result.scalar_one_or_none()

    async def add_state(self, state: WorkflowState) -> WorkflowState:
        self.session.add(state)
        await self.session.flush()
        await self.session.refresh(state)
        return state

    async def list_actions(self, workflow_version_id: UUID) -> list[WorkflowAction]:
        result = await self.session.execute(
            select(WorkflowAction)
            .where(WorkflowAction.workflow_version_id == workflow_version_id)
            .order_by(WorkflowAction.action_code)
        )
        return list(result.scalars().all())

    async def get_action(self, workflow_version_id: UUID, action_code: str) -> WorkflowAction | None:
        result = await self.session.execute(
            select(WorkflowAction).where(
                WorkflowAction.workflow_version_id == workflow_version_id,
                WorkflowAction.action_code == action_code,
            )
        )
        return result.scalar_one_or_none()

    async def add_action(self, action: WorkflowAction) -> WorkflowAction:
        self.session.add(action)
        await self.session.flush()
        await self.session.refresh(action)
        return action

    async def list_transitions(self, workflow_definition_id: UUID) -> list[WorkflowTransition]:
        result = await self.session.execute(
            select(WorkflowTransition)
            .where(WorkflowTransition.workflow_definition_id == workflow_definition_id)
            .order_by(WorkflowTransition.from_state, WorkflowTransition.action_name)
        )
        return list(result.scalars().all())

    async def get_transition(self, workflow_definition_id: UUID, from_state: str, action_name: str) -> WorkflowTransition | None:
        result = await self.session.execute(
            select(WorkflowTransition).where(
                WorkflowTransition.workflow_definition_id == workflow_definition_id,
                WorkflowTransition.from_state == from_state,
                WorkflowTransition.action_name == action_name,
            )
        )
        return result.scalar_one_or_none()

    async def add_transition(self, transition: WorkflowTransition) -> WorkflowTransition:
        self.session.add(transition)
        await self.session.flush()
        await self.session.refresh(transition)
        return transition

    async def get_instance(self, tenant_id: UUID, document_type: str, document_id: UUID) -> WorkflowInstance | None:
        result = await self.session.execute(
            select(WorkflowInstance).where(
                WorkflowInstance.tenant_id == tenant_id,
                WorkflowInstance.document_type == document_type,
                WorkflowInstance.document_id == document_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_instance_by_id(self, workflow_instance_id: UUID) -> WorkflowInstance | None:
        return await self.session.get(WorkflowInstance, workflow_instance_id)

    async def add_instance(self, instance: WorkflowInstance) -> WorkflowInstance:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def list_history(self, workflow_instance_id: UUID) -> list[WorkflowHistory]:
        result = await self.session.execute(
            select(WorkflowHistory)
            .where(WorkflowHistory.workflow_instance_id == workflow_instance_id)
            .order_by(WorkflowHistory.created_at)
        )
        return list(result.scalars().all())

    async def add_history(self, history: WorkflowHistory) -> WorkflowHistory:
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history

    async def list_approval_requests(self, workflow_instance_id: UUID) -> list[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequest)
            .where(ApprovalRequest.workflow_instance_id == workflow_instance_id)
            .order_by(ApprovalRequest.created_at)
        )
        return list(result.scalars().all())

    async def get_approval_request_by_id(self, approval_request_id: UUID) -> ApprovalRequest | None:
        return await self.session.get(ApprovalRequest, approval_request_id)

    async def get_pending_approval_request(self, workflow_instance_id: UUID) -> ApprovalRequest | None:
        result = await self.session.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.workflow_instance_id == workflow_instance_id,
                ApprovalRequest.status == "PENDING",
            )
        )
        return result.scalar_one_or_none()

    async def add_approval_request(self, approval_request: ApprovalRequest) -> ApprovalRequest:
        self.session.add(approval_request)
        await self.session.flush()
        await self.session.refresh(approval_request)
        return approval_request

    async def list_approval_decisions(self, approval_request_id: UUID) -> list[ApprovalDecision]:
        result = await self.session.execute(
            select(ApprovalDecision)
            .where(ApprovalDecision.approval_request_id == approval_request_id)
            .order_by(ApprovalDecision.created_at)
        )
        return list(result.scalars().all())

    async def add_approval_decision(self, approval_decision: ApprovalDecision) -> ApprovalDecision:
        self.session.add(approval_decision)
        await self.session.flush()
        await self.session.refresh(approval_decision)
        return approval_decision
