from datetime import datetime, timezone
from uuid import UUID

from app.core.outbox.service import OutboxService
from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.integration.models.data_mapping import DataMapping
from app.modules.integration.models.external_system import ExternalSystem
from app.modules.integration.models.inbound_message import InboundMessage
from app.modules.integration.models.integration_credential import IntegrationCredential
from app.modules.integration.models.outbound_message import OutboundMessage
from app.modules.integration.models.sync_job import SyncJob
from app.modules.integration.models.sync_log import SyncLog
from app.modules.integration.models.webhook_subscription import WebhookSubscription
from app.modules.integration.repositories.integration_repository import IntegrationRepository
from app.modules.integration.schemas.integration_schema import (
    DataMappingCreate,
    ExternalSystemCreate,
    InboundMessageCreate,
    IntegrationCredentialCreate,
    OutboundMessageCreate,
    SyncJobCreate,
    SyncJobRunCreate,
    SyncLogCreate,
    WebhookReceiveCreate,
    WebhookSubscriptionCreate,
)
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class IntegrationService:
    def __init__(
        self,
        repository: IntegrationRepository,
        tenant_repository: TenantRepository,
        outbox_service: OutboxService | None = None,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.outbox_service = outbox_service

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

    async def list_external_systems(self) -> list[ExternalSystem]:
        return await self.repository.list_external_systems(self._get_tenant_scope())

    async def get_external_system_bundle(self, external_system_id: UUID) -> dict:
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and external_system.tenant_id != tenant_scope:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        return {
            "external_system": external_system,
            "credentials": await self.repository.list_credentials(external_system.id),
            "webhook_subscriptions": await self.repository.list_webhook_subscriptions(external_system_id=external_system.id),
            "data_mappings": await self.repository.list_data_mappings(external_system_id=external_system.id),
            "sync_jobs": await self.repository.list_sync_jobs(external_system_id=external_system.id),
        }

    async def create_external_system(self, payload: ExternalSystemCreate) -> ExternalSystem:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant integrasi tidak ditemukan.")
        existing = await self.repository.get_external_system_by_tenant_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(code="EXTERNAL_SYSTEM_CODE_ALREADY_EXISTS", message="Kode external system sudah digunakan.")
        return await self.repository.add_external_system(
            ExternalSystem(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                system_type=payload.system_type,
                base_url=payload.base_url,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def add_credential(self, external_system_id: UUID, payload: IntegrationCredentialCreate) -> IntegrationCredential:
        bundle = await self.get_external_system_bundle(external_system_id)
        external_system = bundle["external_system"]
        existing = await self.repository.get_credential(external_system.id, payload.credential_name)
        if existing is not None:
            raise ConflictException(code="INTEGRATION_CREDENTIAL_ALREADY_EXISTS", message="Credential integrasi sudah ada.")
        return await self.repository.add_credential(
            IntegrationCredential(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system.id,
                credential_name=payload.credential_name,
                credential_type=payload.credential_type,
                secret_masked=payload.secret_masked,
                config_json=payload.config_json,
                is_active=payload.is_active,
            )
        )

    async def list_webhook_subscriptions(self, external_system_id: UUID | None = None) -> list[WebhookSubscription]:
        return await self.repository.list_webhook_subscriptions(
            tenant_id=self._get_tenant_scope(),
            external_system_id=external_system_id,
        )

    async def create_webhook_subscription(self, payload: WebhookSubscriptionCreate) -> WebhookSubscription:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        existing = await self.repository.get_webhook_subscription_by_name(external_system_id, payload.subscription_name)
        if existing is not None:
            raise ConflictException(code="WEBHOOK_SUBSCRIPTION_ALREADY_EXISTS", message="Webhook subscription sudah ada.")
        return await self.repository.add_webhook_subscription(
            WebhookSubscription(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system.id,
                subscription_name=payload.subscription_name,
                event_type=payload.event_type,
                endpoint_path=payload.endpoint_path,
                signing_secret_masked=payload.signing_secret_masked,
                headers_json=payload.headers_json,
                is_active=payload.is_active,
                last_received_at=None,
                notes=payload.notes,
            )
        )

    async def list_data_mappings(self, external_system_id: UUID | None = None) -> list[DataMapping]:
        return await self.repository.list_data_mappings(tenant_id=self._get_tenant_scope(), external_system_id=external_system_id)

    async def create_data_mapping(self, payload: DataMappingCreate) -> DataMapping:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        existing = await self.repository.get_data_mapping_by_name(external_system_id, payload.mapping_name)
        if existing is not None:
            raise ConflictException(code="DATA_MAPPING_ALREADY_EXISTS", message="Data mapping sudah ada.")
        return await self.repository.add_data_mapping(
            DataMapping(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system.id,
                mapping_name=payload.mapping_name,
                source_entity=payload.source_entity,
                target_entity=payload.target_entity,
                direction=payload.direction,
                mapping_config_json=payload.mapping_config_json,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_sync_jobs(self, external_system_id: UUID | None = None) -> list[SyncJob]:
        return await self.repository.list_sync_jobs(tenant_id=self._get_tenant_scope(), external_system_id=external_system_id)

    async def get_sync_job(self, sync_job_id: UUID) -> SyncJob:
        sync_job = await self.repository.get_sync_job_by_id(sync_job_id)
        if sync_job is None:
            raise NotFoundException(code="SYNC_JOB_NOT_FOUND", message="Sync job tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and sync_job.tenant_id != tenant_scope:
            raise NotFoundException(code="SYNC_JOB_NOT_FOUND", message="Sync job tidak ditemukan.")
        return sync_job

    async def create_sync_job(self, payload: SyncJobCreate) -> SyncJob:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        existing = await self.repository.get_sync_job_by_name(external_system_id, payload.job_name)
        if existing is not None:
            raise ConflictException(code="SYNC_JOB_ALREADY_EXISTS", message="Sync job sudah ada.")
        return await self.repository.add_sync_job(
            SyncJob(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system.id,
                job_name=payload.job_name,
                direction=payload.direction,
                trigger_mode=payload.trigger_mode,
                entity_type=payload.entity_type,
                status="READY",
                schedule_expression=payload.schedule_expression,
                filter_json=payload.filter_json,
                last_run_at=None,
                last_success_at=None,
                next_run_at=payload.next_run_at,
                notes=payload.notes,
            )
        )

    async def list_inbound_messages(self, external_system_id: UUID | None = None) -> list[InboundMessage]:
        return await self.repository.list_inbound_messages(tenant_id=self._get_tenant_scope(), external_system_id=external_system_id)

    async def get_inbound_message(self, inbound_message_id: UUID) -> InboundMessage:
        inbound_message = await self.repository.get_inbound_message_by_id(inbound_message_id)
        if inbound_message is None:
            raise NotFoundException(code="INBOUND_MESSAGE_NOT_FOUND", message="Inbound message tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and inbound_message.tenant_id != tenant_scope:
            raise NotFoundException(code="INBOUND_MESSAGE_NOT_FOUND", message="Inbound message tidak ditemukan.")
        return inbound_message

    async def create_inbound_message(self, payload: InboundMessageCreate) -> dict:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        if not payload.idempotency_key.strip():
            raise BadRequestException(code="INBOUND_IDEMPOTENCY_KEY_REQUIRED", message="idempotency_key wajib diisi.")
        existing = await self.repository.get_inbound_message_by_idempotency(external_system.tenant_id, external_system_id, payload.idempotency_key)
        if existing is not None:
            raise ConflictException(code="INBOUND_MESSAGE_IDEMPOTENCY_CONFLICT", message="idempotency_key inbound sudah digunakan.")
        webhook_subscription_id = UUID(payload.webhook_subscription_id) if payload.webhook_subscription_id else None
        inbound_message = await self.repository.add_inbound_message(
            InboundMessage(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system_id,
                webhook_subscription_id=webhook_subscription_id,
                message_type=payload.message_type,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status=payload.status,
                headers_json=payload.headers_json,
                payload_json=payload.payload_json,
                received_at=payload.received_at,
                processed_at=payload.processed_at,
                notes=payload.notes,
            )
        )
        sync_log = await self.repository.add_sync_log(
            SyncLog(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system_id,
                direction="INBOUND",
                message_type=payload.message_type,
                entity_type="inbound_message",
                entity_id=inbound_message.id,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status=payload.status,
                payload_json=payload.payload_json,
                response_json={},
                processed_at=payload.processed_at,
                notes=payload.notes,
            )
        )
        if self.outbox_service is not None:
            await self.outbox_service.create_event(
                tenant_id=external_system.tenant_id,
                event_name="integration.inbound.received",
                aggregate_type="inbound_message",
                aggregate_id=inbound_message.id,
                payload_json={
                    "external_system_id": str(external_system_id),
                    "message_type": payload.message_type,
                    "external_reference": payload.external_reference,
                    "sync_log_id": str(sync_log.id),
                },
            )
        return {"inbound_message": inbound_message, "sync_log": sync_log}

    async def receive_webhook(self, subscription_id: UUID, payload: WebhookReceiveCreate) -> dict:
        subscription = await self.repository.get_webhook_subscription_by_id(subscription_id)
        if subscription is None or not subscription.is_active:
            raise NotFoundException(code="WEBHOOK_SUBSCRIPTION_NOT_FOUND", message="Webhook subscription tidak ditemukan.")
        received_at = payload.received_at or datetime.now(timezone.utc)
        subscription.last_received_at = received_at
        return await self.create_inbound_message(
            InboundMessageCreate(
                external_system_id=str(subscription.external_system_id),
                webhook_subscription_id=str(subscription.id),
                message_type=payload.message_type,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status="RECEIVED",
                headers_json=payload.headers_json,
                payload_json=payload.payload_json,
                received_at=received_at,
                processed_at=None,
                notes=payload.notes,
            )
        )

    async def list_outbound_messages(self, external_system_id: UUID | None = None) -> list[OutboundMessage]:
        return await self.repository.list_outbound_messages(tenant_id=self._get_tenant_scope(), external_system_id=external_system_id)

    async def get_outbound_message(self, outbound_message_id: UUID) -> OutboundMessage:
        outbound_message = await self.repository.get_outbound_message_by_id(outbound_message_id)
        if outbound_message is None:
            raise NotFoundException(code="OUTBOUND_MESSAGE_NOT_FOUND", message="Outbound message tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and outbound_message.tenant_id != tenant_scope:
            raise NotFoundException(code="OUTBOUND_MESSAGE_NOT_FOUND", message="Outbound message tidak ditemukan.")
        return outbound_message

    async def create_outbound_message(self, payload: OutboundMessageCreate) -> dict:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        if not payload.idempotency_key.strip():
            raise BadRequestException(code="OUTBOUND_IDEMPOTENCY_KEY_REQUIRED", message="idempotency_key wajib diisi.")
        existing = await self.repository.get_outbound_message_by_idempotency(external_system.tenant_id, external_system_id, payload.idempotency_key)
        if existing is not None:
            raise ConflictException(code="OUTBOUND_MESSAGE_IDEMPOTENCY_CONFLICT", message="idempotency_key outbound sudah digunakan.")
        outbound_message = await self.repository.add_outbound_message(
            OutboundMessage(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system_id,
                sync_job_id=UUID(payload.sync_job_id) if payload.sync_job_id else None,
                message_type=payload.message_type,
                entity_type=payload.entity_type,
                entity_id=UUID(payload.entity_id) if payload.entity_id else None,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status=payload.status,
                destination_url=payload.destination_url or external_system.base_url,
                payload_json=payload.payload_json,
                response_json=payload.response_json,
                retry_count=payload.retry_count,
                queued_at=payload.queued_at,
                processed_at=payload.processed_at,
                notes=payload.notes,
            )
        )
        sync_log = await self.repository.add_sync_log(
            SyncLog(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system_id,
                direction="OUTBOUND",
                message_type=payload.message_type,
                entity_type=payload.entity_type,
                entity_id=outbound_message.entity_id,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status=payload.status,
                payload_json=payload.payload_json,
                response_json=payload.response_json,
                processed_at=payload.processed_at,
                notes=payload.notes,
            )
        )
        if self.outbox_service is not None:
            await self.outbox_service.create_event(
                tenant_id=external_system.tenant_id,
                event_name="integration.outbound.queued",
                aggregate_type="outbound_message",
                aggregate_id=outbound_message.id,
                payload_json={
                    "external_system_id": str(external_system_id),
                    "message_type": payload.message_type,
                    "external_reference": payload.external_reference,
                    "sync_log_id": str(sync_log.id),
                },
            )
        return {"outbound_message": outbound_message, "sync_log": sync_log}

    async def run_sync_job(self, sync_job_id: UUID, payload: SyncJobRunCreate) -> dict:
        sync_job = await self.get_sync_job(sync_job_id)
        run_at = datetime.now(timezone.utc)
        sync_job.status = "RUNNING"
        sync_job.last_run_at = run_at
        result = await self.create_outbound_message(
            OutboundMessageCreate(
                external_system_id=str(sync_job.external_system_id),
                sync_job_id=str(sync_job.id),
                message_type=payload.message_type,
                entity_type=sync_job.entity_type,
                entity_id=payload.entity_id,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status="QUEUED",
                destination_url=payload.destination_url,
                payload_json=payload.payload_json,
                response_json=payload.response_json,
                retry_count=0,
                queued_at=run_at,
                processed_at=None,
                notes=payload.notes,
            )
        )
        sync_job.status = "SUCCESS"
        sync_job.last_success_at = run_at
        return {"sync_job": sync_job, **result}

    async def list_sync_logs(self, external_system_id: UUID | None = None, direction: str | None = None) -> list[SyncLog]:
        return await self.repository.list_sync_logs(
            tenant_id=self._get_tenant_scope(),
            external_system_id=external_system_id,
            direction=direction,
        )

    async def get_sync_log(self, sync_log_id: UUID) -> SyncLog:
        sync_log = await self.repository.get_sync_log_by_id(sync_log_id)
        if sync_log is None:
            raise NotFoundException(code="SYNC_LOG_NOT_FOUND", message="Sync log tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and sync_log.tenant_id != tenant_scope:
            raise NotFoundException(code="SYNC_LOG_NOT_FOUND", message="Sync log tidak ditemukan.")
        return sync_log

    async def create_sync_log(self, payload: SyncLogCreate) -> SyncLog:
        external_system_id = UUID(payload.external_system_id)
        external_system = await self.repository.get_external_system_by_id(external_system_id)
        if external_system is None:
            raise NotFoundException(code="EXTERNAL_SYSTEM_NOT_FOUND", message="External system tidak ditemukan.")
        enforce_tenant_write_scope(external_system.tenant_id)
        if not payload.idempotency_key.strip():
            raise BadRequestException(code="INTEGRATION_IDEMPOTENCY_KEY_REQUIRED", message="idempotency_key wajib diisi.")
        existing = await self.repository.get_sync_log_by_idempotency(
            external_system.tenant_id,
            external_system_id,
            payload.idempotency_key,
        )
        if existing is not None:
            raise ConflictException(code="SYNC_LOG_IDEMPOTENCY_CONFLICT", message="idempotency_key sudah pernah digunakan.")
        entity_id = UUID(payload.entity_id) if payload.entity_id else None
        return await self.repository.add_sync_log(
            SyncLog(
                tenant_id=external_system.tenant_id,
                external_system_id=external_system_id,
                direction=payload.direction,
                message_type=payload.message_type,
                entity_type=payload.entity_type,
                entity_id=entity_id,
                external_reference=payload.external_reference,
                idempotency_key=payload.idempotency_key,
                status=payload.status,
                payload_json=payload.payload_json,
                response_json=payload.response_json,
                processed_at=payload.processed_at,
                notes=payload.notes,
            )
        )
