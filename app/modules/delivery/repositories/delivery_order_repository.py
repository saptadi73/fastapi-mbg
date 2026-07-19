from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_order import DeliveryOrder


class DeliveryOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> list[DeliveryOrder]:
        query = select(DeliveryOrder).order_by(DeliveryOrder.created_at.desc())
        if tenant_id is not None:
            query = query.where(DeliveryOrder.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(DeliveryOrder.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, delivery_order_id: UUID) -> DeliveryOrder | None:
        return await self.session.get(DeliveryOrder, delivery_order_id)

    async def list_by_ids(self, delivery_order_ids: list[UUID]) -> list[DeliveryOrder]:
        if not delivery_order_ids:
            return []
        result = await self.session.execute(select(DeliveryOrder).where(DeliveryOrder.id.in_(delivery_order_ids)))
        return list(result.scalars().all())

    async def get_by_id_and_scope(
        self,
        delivery_order_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> DeliveryOrder | None:
        query = select(DeliveryOrder).where(DeliveryOrder.id == delivery_order_id)
        if tenant_id is not None:
            query = query.where(DeliveryOrder.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(DeliveryOrder.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(DeliveryOrder.id)).where(DeliveryOrder.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, delivery_order: DeliveryOrder) -> DeliveryOrder:
        self.session.add(delivery_order)
        await self.session.flush()
        await self.session.refresh(delivery_order)
        return delivery_order
