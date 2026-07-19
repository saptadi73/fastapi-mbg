from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.integration.models.data_mapping import DataMapping
from app.modules.integration.models.external_system import ExternalSystem
from app.modules.integration.models.inbound_message import InboundMessage
from app.modules.integration.models.integration_credential import IntegrationCredential
from app.modules.integration.models.outbound_message import OutboundMessage
from app.modules.integration.models.sync_job import SyncJob
from app.modules.integration.models.sync_log import SyncLog
from app.modules.integration.models.webhook_subscription import WebhookSubscription


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

    async def list_webhook_subscriptions(self, tenant_id: UUID | None = None, external_system_id: UUID | None = None) -> list[WebhookSubscription]:
        query = select(WebhookSubscription).order_by(WebhookSubscription.subscription_name)
        if tenant_id is not None:
            query = query.where(WebhookSubscription.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(WebhookSubscription.external_system_id == external_system_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_webhook_subscription_by_id(self, subscription_id: UUID) -> WebhookSubscription | None:
        return await self.session.get(WebhookSubscription, subscription_id)

    async def get_webhook_subscription_by_name(self, external_system_id: UUID, subscription_name: str) -> WebhookSubscription | None:
        result = await self.session.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.external_system_id == external_system_id,
                WebhookSubscription.subscription_name == subscription_name,
            )
        )
        return result.scalar_one_or_none()

    async def add_webhook_subscription(self, subscription: WebhookSubscription) -> WebhookSubscription:
        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription

    async def list_data_mappings(self, tenant_id: UUID | None = None, external_system_id: UUID | None = None) -> list[DataMapping]:
        query = select(DataMapping).order_by(DataMapping.mapping_name)
        if tenant_id is not None:
            query = query.where(DataMapping.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(DataMapping.external_system_id == external_system_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_data_mapping_by_name(self, external_system_id: UUID, mapping_name: str) -> DataMapping | None:
        result = await self.session.execute(
            select(DataMapping).where(
                DataMapping.external_system_id == external_system_id,
                DataMapping.mapping_name == mapping_name,
            )
        )
        return result.scalar_one_or_none()

    async def add_data_mapping(self, mapping: DataMapping) -> DataMapping:
        self.session.add(mapping)
        await self.session.flush()
        await self.session.refresh(mapping)
        return mapping

    async def list_sync_jobs(self, tenant_id: UUID | None = None, external_system_id: UUID | None = None) -> list[SyncJob]:
        query = select(SyncJob).order_by(SyncJob.job_name)
        if tenant_id is not None:
            query = query.where(SyncJob.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(SyncJob.external_system_id == external_system_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_sync_job_by_id(self, sync_job_id: UUID) -> SyncJob | None:
        return await self.session.get(SyncJob, sync_job_id)

    async def get_sync_job_by_name(self, external_system_id: UUID, job_name: str) -> SyncJob | None:
        result = await self.session.execute(
            select(SyncJob).where(
                SyncJob.external_system_id == external_system_id,
                SyncJob.job_name == job_name,
            )
        )
        return result.scalar_one_or_none()

    async def add_sync_job(self, sync_job: SyncJob) -> SyncJob:
        self.session.add(sync_job)
        await self.session.flush()
        await self.session.refresh(sync_job)
        return sync_job

    async def list_inbound_messages(self, tenant_id: UUID | None = None, external_system_id: UUID | None = None) -> list[InboundMessage]:
        query = select(InboundMessage).order_by(InboundMessage.received_at.desc())
        if tenant_id is not None:
            query = query.where(InboundMessage.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(InboundMessage.external_system_id == external_system_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_inbound_message_by_id(self, inbound_message_id: UUID) -> InboundMessage | None:
        return await self.session.get(InboundMessage, inbound_message_id)

    async def get_inbound_message_by_idempotency(self, tenant_id: UUID, external_system_id: UUID, idempotency_key: str) -> InboundMessage | None:
        result = await self.session.execute(
            select(InboundMessage).where(
                InboundMessage.tenant_id == tenant_id,
                InboundMessage.external_system_id == external_system_id,
                InboundMessage.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def add_inbound_message(self, inbound_message: InboundMessage) -> InboundMessage:
        self.session.add(inbound_message)
        await self.session.flush()
        await self.session.refresh(inbound_message)
        return inbound_message

    async def list_outbound_messages(self, tenant_id: UUID | None = None, external_system_id: UUID | None = None) -> list[OutboundMessage]:
        query = select(OutboundMessage).order_by(OutboundMessage.queued_at.desc())
        if tenant_id is not None:
            query = query.where(OutboundMessage.tenant_id == tenant_id)
        if external_system_id is not None:
            query = query.where(OutboundMessage.external_system_id == external_system_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_outbound_message_by_id(self, outbound_message_id: UUID) -> OutboundMessage | None:
        return await self.session.get(OutboundMessage, outbound_message_id)

    async def get_outbound_message_by_idempotency(self, tenant_id: UUID, external_system_id: UUID, idempotency_key: str) -> OutboundMessage | None:
        result = await self.session.execute(
            select(OutboundMessage).where(
                OutboundMessage.tenant_id == tenant_id,
                OutboundMessage.external_system_id == external_system_id,
                OutboundMessage.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def add_outbound_message(self, outbound_message: OutboundMessage) -> OutboundMessage:
        self.session.add(outbound_message)
        await self.session.flush()
        await self.session.refresh(outbound_message)
        return outbound_message

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
