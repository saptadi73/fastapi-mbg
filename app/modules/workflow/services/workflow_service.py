from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.identity.models.user import User
from app.modules.workflow.models.workflow_definition import WorkflowDefinition
from app.modules.workflow.models.workflow_history import WorkflowHistory
from app.modules.workflow.models.workflow_instance import WorkflowInstance
from app.modules.workflow.models.workflow_transition import WorkflowTransition
from app.modules.workflow.repositories.workflow_repository import WorkflowRepository
from app.modules.workflow.schemas.workflow_schema import WorkflowDefinitionCreate, WorkflowTransitionCreate
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class WorkflowService:
    def __init__(self, repository: WorkflowRepository) -> None:
        self.repository = repository

    def _get_tenant_scope(self) -> UUID | None:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            return None
        try:
            return UUID(current_tenant)
        except ValueError as exc:
            raise BadRequestException(
                code="INVALID_TENANT_CONTEXT",
                message="Header X-Tenant-ID tidak valid.",
            ) from exc

    async def list_definitions(self) -> list[WorkflowDefinition]:
        return await self.repository.list_definitions(tenant_id=self._get_tenant_scope())

    async def get_definition_bundle(self, definition_id: UUID) -> dict:
        definition = await self.repository.get_definition_by_id(definition_id)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        return {"definition": definition, "transitions": await self.repository.list_transitions(definition.id)}

    async def create_definition(self, payload: WorkflowDefinitionCreate) -> WorkflowDefinition:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        existing = await self.repository.get_definition_by_document_type(tenant_id, payload.document_type)
        if existing is not None:
            raise ConflictException(
                code="WORKFLOW_DEFINITION_ALREADY_EXISTS",
                message="Workflow definition untuk document type ini sudah ada.",
            )
        return await self.repository.add_definition(
            WorkflowDefinition(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                document_type=payload.document_type,
                initial_state=payload.initial_state,
                is_active=payload.is_active,
            )
        )

    async def add_transition(self, definition_id: UUID, payload: WorkflowTransitionCreate) -> WorkflowTransition:
        definition = await self.repository.get_definition_by_id(definition_id)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        existing = await self.repository.get_transition(definition_id, payload.from_state, payload.action_name)
        if existing is not None:
            raise ConflictException(
                code="WORKFLOW_TRANSITION_ALREADY_EXISTS",
                message="Workflow transition sudah ada.",
            )
        return await self.repository.add_transition(
            WorkflowTransition(
                tenant_id=definition.tenant_id,
                workflow_definition_id=definition.id,
                from_state=payload.from_state,
                action_name=payload.action_name,
                to_state=payload.to_state,
                allowed_role=payload.allowed_role,
                requires_approval=payload.requires_approval,
            )
        )

    async def get_document_workflow(self, tenant_id: UUID, document_type: str, document_id: UUID) -> dict:
        definition = await self.repository.get_definition_by_document_type(tenant_id, document_type)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        instance = await self.repository.get_instance(tenant_id, document_type, document_id)
        if instance is None:
            raise NotFoundException(code="WORKFLOW_INSTANCE_NOT_FOUND", message="Workflow instance tidak ditemukan.")
        return {
            "definition": definition,
            "instance": instance,
            "transitions": await self.repository.list_transitions(definition.id),
            "history": await self.repository.list_history(instance.id),
        }

    async def ensure_definition_with_transitions(
        self,
        tenant_id: UUID,
        *,
        code: str,
        name: str,
        document_type: str,
        initial_state: str,
        transitions: list[dict],
    ) -> WorkflowDefinition:
        definition = await self.repository.get_definition_by_document_type(tenant_id, document_type)
        if definition is None:
            definition = await self.repository.add_definition(
                WorkflowDefinition(
                    tenant_id=tenant_id,
                    code=code,
                    name=name,
                    document_type=document_type,
                    initial_state=initial_state,
                    is_active=True,
                )
            )
        existing_transitions = await self.repository.list_transitions(definition.id)
        existing_keys = {(item.from_state, item.action_name) for item in existing_transitions}
        for item in transitions:
            key = (item["from_state"], item["action_name"])
            if key in existing_keys:
                continue
            await self.repository.add_transition(
                WorkflowTransition(
                    tenant_id=tenant_id,
                    workflow_definition_id=definition.id,
                    from_state=item["from_state"],
                    action_name=item["action_name"],
                    to_state=item["to_state"],
                    allowed_role=item.get("allowed_role"),
                    requires_approval=item.get("requires_approval", False),
                )
            )
        return definition

    async def ensure_instance(
        self,
        *,
        tenant_id: UUID,
        document_type: str,
        document_id: UUID,
        initial_state: str,
        actor: User | None,
        notes: str | None = None,
    ) -> WorkflowInstance:
        definition = await self.repository.get_definition_by_document_type(tenant_id, document_type)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        instance = await self.repository.get_instance(tenant_id, document_type, document_id)
        if instance is not None:
            return instance
        instance = await self.repository.add_instance(
            WorkflowInstance(
                tenant_id=tenant_id,
                workflow_definition_id=definition.id,
                document_type=document_type,
                document_id=document_id,
                current_state=initial_state,
                last_action="CREATE",
            )
        )
        await self.repository.add_history(
            WorkflowHistory(
                tenant_id=tenant_id,
                workflow_instance_id=instance.id,
                from_state=None,
                action_name="CREATE",
                to_state=initial_state,
                actor_user_id=actor.id if actor else None,
                actor_name=actor.full_name if actor else None,
                notes=notes,
            )
        )
        return instance

    async def apply_transition(
        self,
        *,
        tenant_id: UUID,
        document_type: str,
        document_id: UUID,
        action_name: str,
        expected_state: str,
        actor: User | None,
        notes: str | None = None,
    ) -> WorkflowInstance:
        definition = await self.repository.get_definition_by_document_type(tenant_id, document_type)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        instance = await self.repository.get_instance(tenant_id, document_type, document_id)
        if instance is None:
            raise NotFoundException(code="WORKFLOW_INSTANCE_NOT_FOUND", message="Workflow instance tidak ditemukan.")
        if instance.current_state != expected_state:
            raise BadRequestException(
                code="WORKFLOW_INSTANCE_STATE_MISMATCH",
                message="State workflow dokumen tidak sesuai.",
            )
        transition = await self.repository.get_transition(definition.id, expected_state, action_name)
        if transition is None:
            raise BadRequestException(
                code="WORKFLOW_TRANSITION_NOT_ALLOWED",
                message="Transisi workflow tidak diizinkan.",
            )
        instance.last_action = action_name
        instance.current_state = transition.to_state
        await self.repository.add_history(
            WorkflowHistory(
                tenant_id=tenant_id,
                workflow_instance_id=instance.id,
                from_state=expected_state,
                action_name=action_name,
                to_state=transition.to_state,
                actor_user_id=actor.id if actor else None,
                actor_name=actor.full_name if actor else None,
                notes=notes,
            )
        )
        return instance
