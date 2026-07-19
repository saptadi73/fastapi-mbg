from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.integration.models.external_system import ExternalSystem
from app.modules.integration.models.integration_credential import IntegrationCredential
from app.modules.integration.models.sync_log import SyncLog


class IntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_external_systems(self, tenant_id: UUID | None = None) -> list[ExternalSystem]:
        query = select(ExternalSystem).order_by(ExternalSystem.name)
        if tenant_id is not None:
            query = query.where(ExternalSystem.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_external_system_by_id(self, external_system_id: UUID) -> ExternalSystem | None:
        return await self.session.get(ExternalSystem, external_system_id)

    async def get_external_system_by_tenant_code(self, tenant_id: UUID, code: str) -> ExternalSystem | None:
        result = await self.session.execute(
            select(ExternalSystem).where(
                ExternalSystem.tenant_id == tenant_id,
                ExternalSystem.code == code,
            )
        )
        return result.scalar_one_or_none()

    async def add_external_system(self, system: ExternalSystem) -> ExternalSystem:
        self.session.add(system)
        await self.session.flush()
        await self.session.refresh(system)
        return system

    async def list_credentials(self, external_system_id: UUID) -> list[IntegrationCredential]:
        result = await self.session.execute(
            select(IntegrationCredential)
            .where(IntegrationCredential.external_system_id == external_system_id)
            .order_by(IntegrationCredential.credential_name)
        )
        return list(result.scalars().all())

    async def get_credential(self, external_system_id: UUID, credential_name: str) -> IntegrationCredential | None:
        result = await self.session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.external_system_id == external_system_id,
                IntegrationCredential.credential_name == credential_name,
            )
        )
        return result.scalar_one_or_none()

    async def add_credential(self, credential: IntegrationCredential) -> IntegrationCredential:
        self.session.add(credential)
        await self.session.flush()
        await self.session.refresh(credential)
        return credential

    async def list_sync_logs(
        self,
        tenant_id: UUID | None = None,
        external_system_id: UUID | None = None,
        direction: str | None = None,
    ) -> list[SyncLog]:
        query = select(SyncLog).order_by(SyncLog.created_at.desc())
        if tenant_id is not None:
            query = query.where(SyncLog.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(SyncLog.external_system_id == external_system_id)
        if direction is not None:
            query = query.where(SyncLog.direction == direction)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_sync_log_by_id(self, sync_log_id: UUID) -> SyncLog | None:
        return await self.session.get(SyncLog, sync_log_id)

    async def get_sync_log_by_idempotency(self, tenant_id: UUID, external_system_id: UUID, idempotency_key: str) -> SyncLog | None:
        result = await self.session.execute(
            select(SyncLog).where(
                SyncLog.tenant_id == tenant_id,
                SyncLog.external_system_id == external_system_id,
                SyncLog.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def add_sync_log(self, sync_log: SyncLog) -> SyncLog:
        self.session.add(sync_log)
        await self.session.flush()
        await self.session.refresh(sync_log)
        return sync_log
