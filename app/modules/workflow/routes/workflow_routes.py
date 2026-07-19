from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.workflow.repositories.workflow_repository import WorkflowRepository
from app.modules.workflow.schemas.workflow_schema import (
    WorkflowBundleRead,
    WorkflowDefinitionCreate,
    WorkflowDefinitionRead,
    WorkflowInstanceBundleRead,
    WorkflowTransitionCreate,
    WorkflowTransitionRead,
)
from app.modules.workflow.services.workflow_service import WorkflowService
from app.support.exceptions.base import BadRequestException
from app.support.responses.envelope import success_response

router = APIRouter()


def get_workflow_service(session: AsyncSession = Depends(get_db_session)) -> WorkflowService:
    return WorkflowService(WorkflowRepository(session))


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/definitions")
async def list_workflow_definitions(request: Request, service: WorkflowService = Depends(get_workflow_service)) -> dict:
    items = [WorkflowDefinitionRead.model_validate(item) for item in await service.list_definitions()]
    return success_response(
        code="WORKFLOW_DEFINITION_LIST_FOUND",
        message="Daftar workflow definition berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/definitions/{definition_id}")
async def get_workflow_definition(
    definition_id: UUID,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    bundle = await service.get_definition_bundle(definition_id)
    return success_response(
        code="WORKFLOW_DEFINITION_FOUND",
        message="Detail workflow definition berhasil diambil.",
        data=WorkflowBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/definitions", status_code=status.HTTP_201_CREATED)
async def create_workflow_definition(
    payload: WorkflowDefinitionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_workflow_service(session)
    definition = await service.create_definition(payload)
    await get_audit_service(session).record_event(
        event_type="CONFIGURATION",
        module_name="workflow",
        action_name="CREATE_DEFINITION",
        summary="Workflow definition dibuat.",
        actor=actor,
        tenant_id=definition.tenant_id,
        entity_type="workflow_definition",
        entity_id=definition.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"document_type": definition.document_type, "code": definition.code},
    )
    await session.commit()
    return success_response(
        code="WORKFLOW_DEFINITION_CREATED",
        message="Workflow definition berhasil dibuat.",
        data=WorkflowDefinitionRead.model_validate(definition),
        meta={"request_id": request.state.request_id},
    )


@router.post("/definitions/{definition_id}/transitions", status_code=status.HTTP_201_CREATED)
async def create_workflow_transition(
    definition_id: UUID,
    payload: WorkflowTransitionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_workflow_service(session)
    transition = await service.add_transition(definition_id, payload)
    await get_audit_service(session).record_event(
        event_type="CONFIGURATION",
        module_name="workflow",
        action_name="CREATE_TRANSITION",
        summary="Workflow transition dibuat.",
        actor=actor,
        tenant_id=transition.tenant_id,
        entity_type="workflow_transition",
        entity_id=transition.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"from_state": payload.from_state, "action_name": payload.action_name, "to_state": payload.to_state},
    )
    await session.commit()
    return success_response(
        code="WORKFLOW_TRANSITION_CREATED",
        message="Workflow transition berhasil dibuat.",
        data=WorkflowTransitionRead.model_validate(transition),
        meta={"request_id": request.state.request_id},
    )


@router.get("/documents/{document_type}/{document_id}")
async def get_document_workflow(
    document_type: str,
    document_id: UUID,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    tenant_id = service._get_tenant_scope()
    if tenant_id is None:
        raise BadRequestException(
            code="WORKFLOW_TENANT_CONTEXT_REQUIRED",
            message="Header X-Tenant-ID wajib dikirim untuk melihat workflow dokumen.",
        )
    bundle = await service.get_document_workflow(tenant_id, document_type, document_id)
    return success_response(
        code="WORKFLOW_INSTANCE_FOUND",
        message="Workflow dokumen berhasil diambil.",
        data=WorkflowInstanceBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["history"])},
    )
