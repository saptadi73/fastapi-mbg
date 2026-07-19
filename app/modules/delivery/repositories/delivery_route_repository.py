from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_route import DeliveryRoute


class DeliveryRouteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[DeliveryRoute]:
        query = select(DeliveryRoute).order_by(DeliveryRoute.created_at.desc())
        if tenant_id is not None:
            query = query.where(DeliveryRoute.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(DeliveryRoute.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, route_id: UUID) -> DeliveryRoute | None:
        return await self.session.get(DeliveryRoute, route_id)

    async def get_by_id_and_scope(
        self,
        route_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> DeliveryRoute | None:
        query = select(DeliveryRoute).where(DeliveryRoute.id == route_id)
        if tenant_id is not None:
            query = query.where(DeliveryRoute.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(DeliveryRoute.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(DeliveryRoute.id)).where(DeliveryRoute.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, delivery_route: DeliveryRoute) -> DeliveryRoute:
        self.session.add(delivery_route)
        await self.session.flush()
        await self.session.refresh(delivery_route)
        return delivery_route
