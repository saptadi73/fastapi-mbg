from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models.audit_event import AuditEvent


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_events(
        self,
        *,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
        module_name: str | None = None,
        event_type: str | None = None,
    ) -> list[AuditEvent]:
        query = select(AuditEvent).order_by(AuditEvent.occurred_at.desc(), AuditEvent.created_at.desc())
        if tenant_id is not None:
            query = query.where(AuditEvent.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AuditEvent.sppg_id == sppg_id)
        if module_name is not None:
            query = query.where(AuditEvent.module_name == module_name)
        if event_type is not None:
            query = query.where(AuditEvent.event_type == event_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: UUID) -> AuditEvent | None:
        return await self.session.get(AuditEvent, event_id)

    async def add(self, event: AuditEvent) -> AuditEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event
