from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.outbox.models.outbox_event import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_events(self, tenant_id: UUID | None = None, status: str | None = None) -> list[OutboxEvent]:
        query = select(OutboxEvent).order_by(OutboxEvent.created_at.desc())
        if tenant_id is not None:
            query = query.where(OutboxEvent.tenant_id == tenant_id)
        if status is not None:
            query = query.where(OutboxEvent.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: UUID) -> OutboxEvent | None:
        return await self.session.get(OutboxEvent, event_id)

    async def add(self, event: OutboxEvent) -> OutboxEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event
