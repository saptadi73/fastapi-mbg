from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.integration.repositories.integration_repository import IntegrationRepository
from app.modules.integration.schemas.integration_schema import (
    ExternalSystemBundleRead,
    ExternalSystemCreate,
    ExternalSystemRead,
    IntegrationCredentialCreate,
    IntegrationCredentialRead,
    SyncLogCreate,
    SyncLogRead,
)
from app.modules.integration.services.integration_service import IntegrationService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_integration_service(session: AsyncSession = Depends(get_db_session)) -> IntegrationService:
    return IntegrationService(IntegrationRepository(session), TenantRepository(session))


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/external-systems")
async def list_external_systems(request: Request, service: IntegrationService = Depends(get_integration_service)) -> dict:
    items = [ExternalSystemRead.model_validate(item) for item in await service.list_external_systems()]
    return success_response(
        code="EXTERNAL_SYSTEM_LIST_FOUND",
        message="Daftar external system berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/external-systems/{external_system_id}")
async def get_external_system(
    external_system_id: UUID,
    request: Request,
    service: IntegrationService = Depends(get_integration_service),
) -> dict:
    bundle = await service.get_external_system_bundle(external_system_id)
    return success_response(
        code="EXTERNAL_SYSTEM_FOUND",
        message="Detail external system berhasil diambil.",
        data=ExternalSystemBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/external-systems", status_code=status.HTTP_201_CREATED)
async def create_external_system(
    payload: ExternalSystemCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    external_system = await service.create_external_system(payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_EXTERNAL_SYSTEM",
        summary="External system dibuat.",
        actor=actor,
        tenant_id=external_system.tenant_id,
        entity_type="external_system",
        entity_id=external_system.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": payload.code, "system_type": payload.system_type},
    )
    await session.commit()
    return success_response(
        code="EXTERNAL_SYSTEM_CREATED",
        message="External system berhasil dibuat.",
        data=ExternalSystemRead.model_validate(external_system),
        meta={"request_id": request.state.request_id},
    )


@router.post("/external-systems/{external_system_id}/credentials", status_code=status.HTTP_201_CREATED)
async def create_integration_credential(
    external_system_id: UUID,
    payload: IntegrationCredentialCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    credential = await service.add_credential(external_system_id, payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_CREDENTIAL",
        summary="Credential integrasi dibuat.",
        actor=actor,
        tenant_id=credential.tenant_id,
        entity_type="integration_credential",
        entity_id=credential.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"credential_name": payload.credential_name, "credential_type": payload.credential_type},
    )
    await session.commit()
    return success_response(
        code="INTEGRATION_CREDENTIAL_CREATED",
        message="Credential integrasi berhasil dibuat.",
        data=IntegrationCredentialRead.model_validate(credential),
        meta={"request_id": request.state.request_id},
    )


@router.get("/sync-logs")
async def list_sync_logs(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    direction: str | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [
        SyncLogRead.model_validate(item)
        for item in await service.list_sync_logs(external_system_id=external_system_id, direction=direction)
    ]
    return success_response(
        code="SYNC_LOG_LIST_FOUND",
        message="Daftar sync log berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/sync-logs/{sync_log_id}")
async def get_sync_log(
    sync_log_id: UUID,
    request: Request,
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    sync_log = await service.get_sync_log(sync_log_id)
    return success_response(
        code="SYNC_LOG_FOUND",
        message="Detail sync log berhasil diambil.",
        data=SyncLogRead.model_validate(sync_log),
        meta={"request_id": request.state.request_id},
    )


@router.post("/sync-logs", status_code=status.HTTP_201_CREATED)
async def create_sync_log(
    payload: SyncLogCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    sync_log = await service.create_sync_log(payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_SYNC_LOG",
        summary="Sync log integrasi dibuat.",
        actor=actor,
        tenant_id=sync_log.tenant_id,
        entity_type="sync_log",
        entity_id=sync_log.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"direction": payload.direction, "message_type": payload.message_type, "idempotency_key": payload.idempotency_key},
    )
    await session.commit()
    return success_response(
        code="SYNC_LOG_CREATED",
        message="Sync log berhasil dibuat.",
        data=SyncLogRead.model_validate(sync_log),
        meta={"request_id": request.state.request_id},
    )
