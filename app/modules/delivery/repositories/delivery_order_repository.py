from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_order import DeliveryOrder


class DeliveryOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[DeliveryOrder]:
        result = await self.session.execute(select(DeliveryOrder).order_by(DeliveryOrder.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, delivery_order_id: UUID) -> DeliveryOrder | None:
        return await self.session.get(DeliveryOrder, delivery_order_id)

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(DeliveryOrder.id)).where(DeliveryOrder.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, delivery_order: DeliveryOrder) -> DeliveryOrder:
        self.session.add(delivery_order)
        await self.session.flush()
        await self.session.refresh(delivery_order)
        return delivery_order
