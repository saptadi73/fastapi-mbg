from datetime import datetime, timezone
from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.identity.models.user import User
from app.modules.workflow.models.approval_decision import ApprovalDecision
from app.modules.workflow.models.approval_request import ApprovalRequest
from app.modules.workflow.models.workflow_action import WorkflowAction
from app.modules.workflow.models.workflow_definition import WorkflowDefinition
from app.modules.workflow.models.workflow_history import WorkflowHistory
from app.modules.workflow.models.workflow_instance import WorkflowInstance
from app.modules.workflow.models.workflow_state import WorkflowState
from app.modules.workflow.models.workflow_transition import WorkflowTransition
from app.modules.workflow.models.workflow_version import WorkflowVersion
from app.modules.workflow.repositories.workflow_repository import WorkflowRepository
from app.modules.workflow.schemas.workflow_schema import (
    ApprovalDecisionCreate,
    ApprovalRequestCreate,
    WorkflowActionCreate,
    WorkflowDefinitionCreate,
    WorkflowStateCreate,
    WorkflowTransitionCreate,
    WorkflowVersionCreate,
)
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class WorkflowService:
    def __init__(self, repository: WorkflowRepository) -> None:
        self.repository = repository

    async def _ensure_definition_version_structure(
        self,
        definition: WorkflowDefinition,
        *,
        initial_state: str,
        transitions: list[dict] | None = None,
    ) -> WorkflowVersion:
        version = await self.repository.get_active_version(definition.id)
        if version is None:
            existing_versions = await self.repository.list_versions(definition.id)
            version = await self.repository.add_version(
                WorkflowVersion(
                    tenant_id=definition.tenant_id,
                    workflow_definition_id=definition.id,
                    version_number=max((item.version_number for item in existing_versions), default=0) + 1,
                    status="ACTIVE",
                    is_active=True,
                    notes="Auto-generated version",
                )
            )
        if await self.repository.get_state(version.id, initial_state) is None:
            await self.repository.add_state(
                WorkflowState(
                    tenant_id=definition.tenant_id,
                    workflow_version_id=version.id,
                    state_code=initial_state,
                    state_name=initial_state.replace("_", " ").title(),
                    sequence_number=1,
                    is_initial=True,
                    is_terminal=False,
                    sla_hours=None,
                )
            )
        for index, item in enumerate(transitions or [], start=2):
            if await self.repository.get_state(version.id, item["from_state"]) is None:
                await self.repository.add_state(
                    WorkflowState(
                        tenant_id=definition.tenant_id,
                        workflow_version_id=version.id,
                        state_code=item["from_state"],
                        state_name=item["from_state"].replace("_", " ").title(),
                        sequence_number=index,
                        is_initial=item["from_state"] == initial_state,
                        is_terminal=False,
                        sla_hours=None,
                    )
                )
            if await self.repository.get_state(version.id, item["to_state"]) is None:
                await self.repository.add_state(
                    WorkflowState(
                        tenant_id=definition.tenant_id,
                        workflow_version_id=version.id,
                        state_code=item["to_state"],
                        state_name=item["to_state"].replace("_", " ").title(),
                        sequence_number=index + 1,
                        is_initial=False,
                        is_terminal=False,
                        sla_hours=None,
                    )
                )
            if await self.repository.get_action(version.id, item["action_name"]) is None:
                await self.repository.add_action(
                    WorkflowAction(
                        tenant_id=definition.tenant_id,
                        workflow_version_id=version.id,
                        action_code=item["action_name"],
                        action_name=item["action_name"].replace("_", " ").title(),
                        allowed_role=item.get("allowed_role"),
                        requires_approval=item.get("requires_approval", False),
                        is_active=True,
                    )
                )
        return version

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
        versions = await self.repository.list_versions(definition.id)
        active_version = await self.repository.get_active_version(definition.id)
        version_id = active_version.id if active_version is not None else None
        states = await self.repository.list_states(version_id) if version_id is not None else []
        actions = await self.repository.list_actions(version_id) if version_id is not None else []
        return {
            "definition": definition,
            "versions": versions,
            "states": states,
            "actions": actions,
            "transitions": await self.repository.list_transitions(definition.id),
        }

    async def create_definition(self, payload: WorkflowDefinitionCreate) -> WorkflowDefinition:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        existing = await self.repository.get_definition_by_document_type(tenant_id, payload.document_type)
        if existing is not None:
            raise ConflictException(
                code="WORKFLOW_DEFINITION_ALREADY_EXISTS",
                message="Workflow definition untuk document type ini sudah ada.",
            )
        definition = await self.repository.add_definition(
            WorkflowDefinition(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                document_type=payload.document_type,
                initial_state=payload.initial_state,
                is_active=payload.is_active,
            )
        )
        await self.repository.add_version(
            WorkflowVersion(
                tenant_id=tenant_id,
                workflow_definition_id=definition.id,
                version_number=1,
                status="ACTIVE",
                is_active=True,
                notes="Initial workflow version",
            )
        )
        return definition

    async def create_version(self, definition_id: UUID, payload: WorkflowVersionCreate) -> WorkflowVersion:
        definition = await self.repository.get_definition_by_id(definition_id)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        versions = await self.repository.list_versions(definition.id)
        next_number = max((item.version_number for item in versions), default=0) + 1
        if payload.is_active:
            for version in versions:
                version.is_active = False
        return await self.repository.add_version(
            WorkflowVersion(
                tenant_id=definition.tenant_id,
                workflow_definition_id=definition.id,
                version_number=next_number,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def add_state(self, version_id: UUID, payload: WorkflowStateCreate) -> WorkflowState:
        version = await self.repository.get_version_by_id(version_id)
        if version is None:
            raise NotFoundException(code="WORKFLOW_VERSION_NOT_FOUND", message="Workflow version tidak ditemukan.")
        existing = await self.repository.get_state(version.id, payload.state_code)
        if existing is not None:
            raise ConflictException(code="WORKFLOW_STATE_ALREADY_EXISTS", message="Workflow state sudah ada.")
        if payload.is_initial:
            for state in await self.repository.list_states(version.id):
                state.is_initial = False
        return await self.repository.add_state(
            WorkflowState(
                tenant_id=version.tenant_id,
                workflow_version_id=version.id,
                state_code=payload.state_code,
                state_name=payload.state_name,
                sequence_number=payload.sequence_number,
                is_initial=payload.is_initial,
                is_terminal=payload.is_terminal,
                sla_hours=payload.sla_hours,
            )
        )

    async def add_action(self, version_id: UUID, payload: WorkflowActionCreate) -> WorkflowAction:
        version = await self.repository.get_version_by_id(version_id)
        if version is None:
            raise NotFoundException(code="WORKFLOW_VERSION_NOT_FOUND", message="Workflow version tidak ditemukan.")
        existing = await self.repository.get_action(version.id, payload.action_code)
        if existing is not None:
            raise ConflictException(code="WORKFLOW_ACTION_ALREADY_EXISTS", message="Workflow action sudah ada.")
        return await self.repository.add_action(
            WorkflowAction(
                tenant_id=version.tenant_id,
                workflow_version_id=version.id,
                action_code=payload.action_code,
                action_name=payload.action_name,
                allowed_role=payload.allowed_role,
                requires_approval=payload.requires_approval,
                is_active=payload.is_active,
            )
        )

    async def add_transition(self, definition_id: UUID, payload: WorkflowTransitionCreate) -> WorkflowTransition:
        definition = await self.repository.get_definition_by_id(definition_id)
        if definition is None:
            raise NotFoundException(code="WORKFLOW_DEFINITION_NOT_FOUND", message="Workflow definition tidak ditemukan.")
        version = await self.repository.get_active_version(definition.id)
        if version is None:
            raise NotFoundException(code="WORKFLOW_VERSION_NOT_FOUND", message="Workflow version aktif tidak ditemukan.")
        existing = await self.repository.get_transition(definition_id, payload.from_state, payload.action_name)
        if existing is not None:
            raise ConflictException(
                code="WORKFLOW_TRANSITION_ALREADY_EXISTS",
                message="Workflow transition sudah ada.",
            )
        if await self.repository.get_state(version.id, payload.from_state) is None:
            await self.repository.add_state(
                WorkflowState(
                    tenant_id=definition.tenant_id,
                    workflow_version_id=version.id,
                    state_code=payload.from_state,
                    state_name=payload.from_state.replace("_", " ").title(),
                    sequence_number=1,
                    is_initial=payload.from_state == definition.initial_state,
                    is_terminal=False,
                    sla_hours=None,
                )
            )
        if await self.repository.get_state(version.id, payload.to_state) is None:
            await self.repository.add_state(
                WorkflowState(
                    tenant_id=definition.tenant_id,
                    workflow_version_id=version.id,
                    state_code=payload.to_state,
                    state_name=payload.to_state.replace("_", " ").title(),
                    sequence_number=2,
                    is_initial=False,
                    is_terminal=False,
                    sla_hours=None,
                )
            )
        if await self.repository.get_action(version.id, payload.action_name) is None:
            await self.repository.add_action(
                WorkflowAction(
                    tenant_id=definition.tenant_id,
                    workflow_version_id=version.id,
                    action_code=payload.action_name,
                    action_name=payload.action_name.replace("_", " ").title(),
                    allowed_role=payload.allowed_role,
                    requires_approval=payload.requires_approval,
                    is_active=True,
                )
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
        if instance.workflow_version_id is None:
            active_version = await self.repository.get_active_version(definition.id)
            if active_version is not None:
                instance.workflow_version_id = active_version.id
        version = await self.repository.get_version_by_id(instance.workflow_version_id) if instance.workflow_version_id else await self.repository.get_active_version(definition.id)
        states = await self.repository.list_states(version.id) if version is not None else []
        actions = await self.repository.list_actions(version.id) if version is not None else []
        approval_requests = await self.repository.list_approval_requests(instance.id)
        approval_decisions = []
        for approval_request in approval_requests:
            approval_decisions.extend(await self.repository.list_approval_decisions(approval_request.id))
        return {
            "definition": definition,
            "instance": instance,
            "version": version,
            "states": states,
            "actions": actions,
            "transitions": await self.repository.list_transitions(definition.id),
            "history": await self.repository.list_history(instance.id),
            "approval_requests": approval_requests,
            "approval_decisions": approval_decisions,
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
        await self._ensure_definition_version_structure(
            definition,
            initial_state=initial_state,
            transitions=transitions,
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
            if instance.workflow_version_id is None:
                active_version = await self.repository.get_active_version(definition.id)
                if active_version is not None:
                    instance.workflow_version_id = active_version.id
            return instance
        active_version = await self.repository.get_active_version(definition.id)
        instance = await self.repository.add_instance(
            WorkflowInstance(
                tenant_id=tenant_id,
                workflow_definition_id=definition.id,
                workflow_version_id=active_version.id if active_version is not None else None,
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
                approval_request_id=None,
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
        if transition.requires_approval:
            existing_request = await self.repository.get_pending_approval_request(instance.id)
            if existing_request is not None:
                raise ConflictException(
                    code="WORKFLOW_APPROVAL_ALREADY_PENDING",
                    message="Masih ada approval request yang belum diputuskan.",
                )
            approval_request = await self.repository.add_approval_request(
                ApprovalRequest(
                    tenant_id=tenant_id,
                    workflow_instance_id=instance.id,
                    requested_state=transition.to_state,
                    requested_action=action_name,
                    requested_by_user_id=actor.id if actor else None,
                    requested_by_name=actor.full_name if actor else None,
                    status="PENDING",
                    due_at=None,
                    notes=notes,
                )
            )
            instance.last_action = f"{action_name}_REQUESTED"
            await self.repository.add_history(
                WorkflowHistory(
                    tenant_id=tenant_id,
                    workflow_instance_id=instance.id,
                    approval_request_id=approval_request.id,
                    from_state=expected_state,
                    action_name=f"{action_name}_REQUESTED",
                    to_state=expected_state,
                    actor_user_id=actor.id if actor else None,
                    actor_name=actor.full_name if actor else None,
                    notes=notes,
                )
            )
            return instance
        instance.last_action = action_name
        instance.current_state = transition.to_state
        await self.repository.add_history(
            WorkflowHistory(
                tenant_id=tenant_id,
                workflow_instance_id=instance.id,
                approval_request_id=None,
                from_state=expected_state,
                action_name=action_name,
                to_state=transition.to_state,
                actor_user_id=actor.id if actor else None,
                actor_name=actor.full_name if actor else None,
                notes=notes,
            )
        )
        return instance

    async def create_approval_request(self, workflow_instance_id: UUID, payload: ApprovalRequestCreate, actor: User | None) -> ApprovalRequest:
        instance = await self.repository.get_instance_by_id(workflow_instance_id)
        if instance is None:
            raise NotFoundException(code="WORKFLOW_INSTANCE_NOT_FOUND", message="Workflow instance tidak ditemukan.")
        if await self.repository.get_pending_approval_request(workflow_instance_id) is not None:
            raise ConflictException(code="WORKFLOW_APPROVAL_ALREADY_PENDING", message="Approval request masih pending.")
        return await self.repository.add_approval_request(
            ApprovalRequest(
                tenant_id=instance.tenant_id,
                workflow_instance_id=instance.id,
                requested_state=instance.current_state,
                requested_action="MANUAL_APPROVAL",
                requested_by_user_id=actor.id if actor else None,
                requested_by_name=actor.full_name if actor else None,
                status="PENDING",
                due_at=payload.due_at,
                notes=payload.notes,
            )
        )

    async def decide_approval_request(self, approval_request_id: UUID, payload: ApprovalDecisionCreate, actor: User | None) -> dict:
        approval_request = await self.repository.get_approval_request_by_id(approval_request_id)
        if approval_request is None:
            raise NotFoundException(code="APPROVAL_REQUEST_NOT_FOUND", message="Approval request tidak ditemukan.")
        if approval_request.status != "PENDING":
            raise BadRequestException(code="APPROVAL_REQUEST_NOT_PENDING", message="Approval request sudah diputuskan.")
        instance = await self.repository.get_instance_by_id(approval_request.workflow_instance_id)
        if instance is None:
            raise NotFoundException(code="WORKFLOW_INSTANCE_NOT_FOUND", message="Workflow instance tidak ditemukan.")
        decision = await self.repository.add_approval_decision(
            ApprovalDecision(
                tenant_id=approval_request.tenant_id,
                approval_request_id=approval_request.id,
                decision=payload.decision,
                decision_by_user_id=actor.id if actor else None,
                decision_by_name=actor.full_name if actor else None,
                decision_at=datetime.now(timezone.utc),
                notes=payload.notes,
            )
        )
        normalized_decision = payload.decision.upper()
        if normalized_decision == "APPROVED":
            from_state = instance.current_state
            instance.current_state = approval_request.requested_state
            instance.last_action = approval_request.requested_action
            approval_request.status = "APPROVED"
            await self.repository.add_history(
                WorkflowHistory(
                    tenant_id=approval_request.tenant_id,
                    workflow_instance_id=instance.id,
                    approval_request_id=approval_request.id,
                    from_state=from_state,
                    action_name=approval_request.requested_action,
                    to_state=approval_request.requested_state,
                    actor_user_id=actor.id if actor else None,
                    actor_name=actor.full_name if actor else None,
                    notes=payload.notes,
                )
            )
        elif normalized_decision == "REJECTED":
            approval_request.status = "REJECTED"
            await self.repository.add_history(
                WorkflowHistory(
                    tenant_id=approval_request.tenant_id,
                    workflow_instance_id=instance.id,
                    approval_request_id=approval_request.id,
                    from_state=instance.current_state,
                    action_name=f"{approval_request.requested_action}_REJECTED",
                    to_state=instance.current_state,
                    actor_user_id=actor.id if actor else None,
                    actor_name=actor.full_name if actor else None,
                    notes=payload.notes,
                )
            )
        else:
            raise BadRequestException(code="APPROVAL_DECISION_INVALID", message="Decision harus APPROVED atau REJECTED.")
        return {"approval_request": approval_request, "approval_decision": decision, "instance": instance}
