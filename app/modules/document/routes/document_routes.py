from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.document.repositories.document_repository import DocumentRepository
from app.modules.document.schemas.document_schema import (
    DocumentBundleRead,
    DocumentCreate,
    DocumentLinkCreate,
    DocumentLinkRead,
    DocumentRead,
    DocumentVersionCreate,
    DocumentVersionRead,
)
from app.modules.document.services.document_service import DocumentService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_document_service(session: AsyncSession = Depends(get_db_session)) -> DocumentService:
    return DocumentService(
        DocumentRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("")
async def list_documents(request: Request, service: DocumentService = Depends(get_document_service)) -> dict:
    items = [DocumentRead.model_validate(item) for item in await service.list_documents()]
    return success_response(
        code="DOCUMENT_LIST_FOUND",
        message="Daftar dokumen berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{document_id}")
async def get_document(
    document_id: UUID,
    request: Request,
    service: DocumentService = Depends(get_document_service),
) -> dict:
    bundle = await service.get_document_bundle(document_id)
    return success_response(
        code="DOCUMENT_FOUND",
        message="Detail dokumen berhasil diambil.",
        data=DocumentBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "finance_manager")),
) -> dict:
    service = get_document_service(session)
    document = await service.create_document(payload)
    await get_audit_service(session).record_event(
        event_type="DOCUMENT",
        module_name="document",
        action_name="CREATE_DOCUMENT",
        summary="Dokumen dibuat.",
        actor=actor,
        tenant_id=document.tenant_id,
        sppg_id=document.sppg_id,
        entity_type="document",
        entity_id=document.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"document_type": payload.document_type, "title": payload.title},
    )
    await session.commit()
    return success_response(
        code="DOCUMENT_CREATED",
        message="Dokumen berhasil dibuat.",
        data=DocumentRead.model_validate(document),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{document_id}/versions", status_code=status.HTTP_201_CREATED)
async def create_document_version(
    document_id: UUID,
    payload: DocumentVersionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "finance_manager")),
) -> dict:
    service = get_document_service(session)
    version = await service.add_version(document_id, payload)
    await get_audit_service(session).record_event(
        event_type="DOCUMENT",
        module_name="document",
        action_name="ADD_VERSION",
        summary="Versi dokumen ditambahkan.",
        actor=actor,
        tenant_id=version.tenant_id,
        entity_type="document_version",
        entity_id=version.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"file_name": payload.file_name, "version_number": version.version_number},
    )
    await session.commit()
    return success_response(
        code="DOCUMENT_VERSION_CREATED",
        message="Versi dokumen berhasil ditambahkan.",
        data=DocumentVersionRead.model_validate(version),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{document_id}/links", status_code=status.HTTP_201_CREATED)
async def create_document_link(
    document_id: UUID,
    payload: DocumentLinkCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "finance_manager")),
) -> dict:
    service = get_document_service(session)
    link = await service.add_link(document_id, payload)
    await get_audit_service(session).record_event(
        event_type="DOCUMENT",
        module_name="document",
        action_name="ADD_LINK",
        summary="Link dokumen ditambahkan.",
        actor=actor,
        tenant_id=link.tenant_id,
        entity_type="document_link",
        entity_id=link.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"linked_entity_type": payload.linked_entity_type, "linked_entity_id": payload.linked_entity_id},
    )
    await session.commit()
    return success_response(
        code="DOCUMENT_LINK_CREATED",
        message="Link dokumen berhasil ditambahkan.",
        data=DocumentLinkRead.model_validate(link),
        meta={"request_id": request.state.request_id},
    )
