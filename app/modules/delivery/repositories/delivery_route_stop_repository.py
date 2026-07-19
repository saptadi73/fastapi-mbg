from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_route_stop import DeliveryRouteStop


class DeliveryRouteStopRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_route(self, route_id: UUID) -> list[DeliveryRouteStop]:
        result = await self.session.execute(
            select(DeliveryRouteStop)
            .where(DeliveryRouteStop.route_id == route_id)
            .order_by(DeliveryRouteStop.stop_sequence)
        )
        return list(result.scalars().all())

    async def get_by_id(self, route_stop_id: UUID) -> DeliveryRouteStop | None:
        return await self.session.get(DeliveryRouteStop, route_stop_id)

    async def add(self, route_stop: DeliveryRouteStop) -> DeliveryRouteStop:
        self.session.add(route_stop)
        await self.session.flush()
        await self.session.refresh(route_stop)
        return route_stop
