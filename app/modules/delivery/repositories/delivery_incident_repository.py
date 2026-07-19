from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_incident import DeliveryIncident


class DeliveryIncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_delivery_order(self, delivery_order_id: UUID) -> list[DeliveryIncident]:
        result = await self.session.execute(
            select(DeliveryIncident)
            .where(DeliveryIncident.delivery_order_id == delivery_order_id)
            .order_by(DeliveryIncident.incident_time)
        )
        return list(result.scalars().all())

    async def list_by_route(self, route_id: UUID) -> list[DeliveryIncident]:
        result = await self.session.execute(
            select(DeliveryIncident).where(DeliveryIncident.route_id == route_id).order_by(DeliveryIncident.incident_time)
        )
        return list(result.scalars().all())

    async def add(self, incident: DeliveryIncident) -> DeliveryIncident:
        self.session.add(incident)
        await self.session.flush()
        await self.session.refresh(incident)
        return incident
