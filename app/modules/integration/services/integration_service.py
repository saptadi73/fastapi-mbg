from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.integration.models.external_system import ExternalSystem
from app.modules.integration.models.integration_credential import IntegrationCredential
from app.modules.integration.models.sync_log import SyncLog
from app.modules.integration.repositories.integration_repository import IntegrationRepository
from app.modules.integration.schemas.integration_schema import (
    ExternalSystemCreate,
    IntegrationCredentialCreate,
    SyncLogCreate,
)
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class IntegrationService:
    def __init__(
        self,
        repository: IntegrationRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository

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
