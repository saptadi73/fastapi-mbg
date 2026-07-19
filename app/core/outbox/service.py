from datetime import datetime, timezone
from uuid import UUID

from app.core.outbox.models.outbox_event import OutboxEvent
from app.core.outbox.repository import OutboxRepository


class OutboxService:
    def __init__(self, repository: OutboxRepository) -> None:
        self.repository = repository

    async def list_events(self, tenant_id: UUID | None = None, status: str | None = None) -> list[OutboxEvent]:
        return await self.repository.list_events(tenant_id=tenant_id, status=status)

    async def create_event(
        self,
        *,
        tenant_id: UUID,
        event_name: str,
        aggregate_type: str,
        aggregate_id: UUID | None,
        payload_json: dict,
        available_at: datetime | None = None,
    ) -> OutboxEvent:
        return await self.repository.add(
            OutboxEvent(
                tenant_id=tenant_id,
                event_name=event_name,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                status="PENDING",
                payload_json=payload_json,
                available_at=available_at or datetime.now(timezone.utc),
                processed_at=None,
                retry_count=0,
                last_error=None,
            )
        )

    async def dispatch_pending(self, tenant_id: UUID | None = None, limit: int = 50) -> list[OutboxEvent]:
        events = await self.repository.list_events(tenant_id=tenant_id, status="PENDING")
        dispatched: list[OutboxEvent] = []
        for event in events[:limit]:
            event.status = "DISPATCHED"
            event.processed_at = datetime.now(timezone.utc)
            event.retry_count += 1
            dispatched.append(event)
        return dispatched
