from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workflow.models.workflow_definition import WorkflowDefinition
from app.modules.workflow.models.workflow_history import WorkflowHistory
from app.modules.workflow.models.workflow_instance import WorkflowInstance
from app.modules.workflow.models.workflow_transition import WorkflowTransition


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
