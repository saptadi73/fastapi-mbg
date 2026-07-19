from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.outbox.repository import OutboxRepository
from app.core.outbox.service import OutboxService
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.integration.repositories.integration_repository import IntegrationRepository
from app.modules.integration.schemas.integration_schema import (
    DataMappingCreate,
    DataMappingRead,
    ExternalSystemBundleRead,
    ExternalSystemCreate,
    ExternalSystemRead,
    InboundMessageCreate,
    InboundMessageRead,
    IntegrationCredentialCreate,
    IntegrationCredentialRead,
    OutboundMessageCreate,
    OutboundMessageRead,
    SyncJobCreate,
    SyncJobRead,
    SyncJobRunCreate,
    SyncLogCreate,
    SyncLogRead,
    WebhookReceiveCreate,
    WebhookSubscriptionCreate,
    WebhookSubscriptionRead,
)
from app.modules.integration.services.integration_service import IntegrationService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_integration_service(session: AsyncSession = Depends(get_db_session)) -> IntegrationService:
    return IntegrationService(IntegrationRepository(session), TenantRepository(session), OutboxService(OutboxRepository(session)))


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


@router.get("/webhook-subscriptions")
async def list_webhook_subscriptions(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [
        WebhookSubscriptionRead.model_validate(item)
        for item in await service.list_webhook_subscriptions(external_system_id=external_system_id)
    ]
    return success_response(
        code="WEBHOOK_SUBSCRIPTION_LIST_FOUND",
        message="Daftar webhook subscription berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/webhook-subscriptions", status_code=status.HTTP_201_CREATED)
async def create_webhook_subscription(
    payload: WebhookSubscriptionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    subscription = await service.create_webhook_subscription(payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_WEBHOOK_SUBSCRIPTION",
        summary="Webhook subscription integrasi dibuat.",
        actor=actor,
        tenant_id=subscription.tenant_id,
        entity_type="webhook_subscription",
        entity_id=subscription.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"subscription_name": payload.subscription_name, "event_type": payload.event_type},
    )
    await session.commit()
    return success_response(
        code="WEBHOOK_SUBSCRIPTION_CREATED",
        message="Webhook subscription berhasil dibuat.",
        data=WebhookSubscriptionRead.model_validate(subscription),
        meta={"request_id": request.state.request_id},
    )


@router.post("/webhook-subscriptions/{subscription_id}/receive", status_code=status.HTTP_201_CREATED)
async def receive_webhook_message(
    subscription_id: UUID,
    payload: WebhookReceiveCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    service = get_integration_service(session)
    result = await service.receive_webhook(subscription_id, payload)
    await session.commit()
    return success_response(
        code="INBOUND_WEBHOOK_RECEIVED",
        message="Webhook inbound berhasil diterima.",
        data={
            "inbound_message": InboundMessageRead.model_validate(result["inbound_message"]),
            "sync_log": SyncLogRead.model_validate(result["sync_log"]),
        },
        meta={"request_id": request.state.request_id},
    )


@router.get("/data-mappings")
async def list_data_mappings(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [DataMappingRead.model_validate(item) for item in await service.list_data_mappings(external_system_id=external_system_id)]
    return success_response(
        code="DATA_MAPPING_LIST_FOUND",
        message="Daftar data mapping berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/data-mappings", status_code=status.HTTP_201_CREATED)
async def create_data_mapping(
    payload: DataMappingCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    mapping = await service.create_data_mapping(payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_DATA_MAPPING",
        summary="Data mapping integrasi dibuat.",
        actor=actor,
        tenant_id=mapping.tenant_id,
        entity_type="data_mapping",
        entity_id=mapping.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"mapping_name": payload.mapping_name, "direction": payload.direction},
    )
    await session.commit()
    return success_response(
        code="DATA_MAPPING_CREATED",
        message="Data mapping berhasil dibuat.",
        data=DataMappingRead.model_validate(mapping),
        meta={"request_id": request.state.request_id},
    )


@router.get("/sync-jobs")
async def list_sync_jobs(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [SyncJobRead.model_validate(item) for item in await service.list_sync_jobs(external_system_id=external_system_id)]
    return success_response(
        code="SYNC_JOB_LIST_FOUND",
        message="Daftar sync job berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/sync-jobs/{sync_job_id}")
async def get_sync_job(
    sync_job_id: UUID,
    request: Request,
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    sync_job = await service.get_sync_job(sync_job_id)
    return success_response(
        code="SYNC_JOB_FOUND",
        message="Detail sync job berhasil diambil.",
        data=SyncJobRead.model_validate(sync_job),
        meta={"request_id": request.state.request_id},
    )


@router.post("/sync-jobs", status_code=status.HTTP_201_CREATED)
async def create_sync_job(
    payload: SyncJobCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    sync_job = await service.create_sync_job(payload)
    await get_audit_service(session).record_event(
        event_type="INTEGRATION",
        module_name="integration",
        action_name="CREATE_SYNC_JOB",
        summary="Sync job integrasi dibuat.",
        actor=actor,
        tenant_id=sync_job.tenant_id,
        entity_type="sync_job",
        entity_id=sync_job.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"job_name": payload.job_name, "entity_type": payload.entity_type},
    )
    await session.commit()
    return success_response(
        code="SYNC_JOB_CREATED",
        message="Sync job berhasil dibuat.",
        data=SyncJobRead.model_validate(sync_job),
        meta={"request_id": request.state.request_id},
    )


@router.post("/sync-jobs/{sync_job_id}/run", status_code=status.HTTP_201_CREATED)
async def run_sync_job(
    sync_job_id: UUID,
    payload: SyncJobRunCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    result = await service.run_sync_job(sync_job_id, payload)
    await session.commit()
    return success_response(
        code="SYNC_JOB_RUN_CREATED",
        message="Sync job berhasil dijalankan.",
        data={
            "sync_job": SyncJobRead.model_validate(result["sync_job"]),
            "outbound_message": OutboundMessageRead.model_validate(result["outbound_message"]),
            "sync_log": SyncLogRead.model_validate(result["sync_log"]),
        },
        meta={"request_id": request.state.request_id},
    )


@router.get("/inbound-messages")
async def list_inbound_messages(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [InboundMessageRead.model_validate(item) for item in await service.list_inbound_messages(external_system_id=external_system_id)]
    return success_response(
        code="INBOUND_MESSAGE_LIST_FOUND",
        message="Daftar inbound message berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/inbound-messages/{inbound_message_id}")
async def get_inbound_message(
    inbound_message_id: UUID,
    request: Request,
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    inbound_message = await service.get_inbound_message(inbound_message_id)
    return success_response(
        code="INBOUND_MESSAGE_FOUND",
        message="Detail inbound message berhasil diambil.",
        data=InboundMessageRead.model_validate(inbound_message),
        meta={"request_id": request.state.request_id},
    )


@router.post("/inbound-messages", status_code=status.HTTP_201_CREATED)
async def create_inbound_message(
    payload: InboundMessageCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    result = await service.create_inbound_message(payload)
    await session.commit()
    return success_response(
        code="INBOUND_MESSAGE_CREATED",
        message="Inbound message berhasil dibuat.",
        data={
            "inbound_message": InboundMessageRead.model_validate(result["inbound_message"]),
            "sync_log": SyncLogRead.model_validate(result["sync_log"]),
        },
        meta={"request_id": request.state.request_id},
    )


@router.get("/outbound-messages")
async def list_outbound_messages(
    request: Request,
    external_system_id: UUID | None = Query(default=None),
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [OutboundMessageRead.model_validate(item) for item in await service.list_outbound_messages(external_system_id=external_system_id)]
    return success_response(
        code="OUTBOUND_MESSAGE_LIST_FOUND",
        message="Daftar outbound message berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/outbound-messages/{outbound_message_id}")
async def get_outbound_message(
    outbound_message_id: UUID,
    request: Request,
    service: IntegrationService = Depends(get_integration_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    outbound_message = await service.get_outbound_message(outbound_message_id)
    return success_response(
        code="OUTBOUND_MESSAGE_FOUND",
        message="Detail outbound message berhasil diambil.",
        data=OutboundMessageRead.model_validate(outbound_message),
        meta={"request_id": request.state.request_id},
    )


@router.post("/outbound-messages", status_code=status.HTTP_201_CREATED)
async def create_outbound_message(
    payload: OutboundMessageCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_integration_service(session)
    result = await service.create_outbound_message(payload)
    await session.commit()
    return success_response(
        code="OUTBOUND_MESSAGE_CREATED",
        message="Outbound message berhasil dibuat.",
        data={
            "outbound_message": OutboundMessageRead.model_validate(result["outbound_message"]),
            "sync_log": SyncLogRead.model_validate(result["sync_log"]),
        },
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
