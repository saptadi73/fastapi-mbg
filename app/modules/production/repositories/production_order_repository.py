from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.production.models.production_order import ProductionOrder


class ProductionOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[ProductionOrder]:
        result = await self.session.execute(select(ProductionOrder).order_by(ProductionOrder.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, production_order_id: UUID) -> ProductionOrder | None:
        return await self.session.get(ProductionOrder, production_order_id)

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(ProductionOrder.id)).where(ProductionOrder.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, production_order: ProductionOrder) -> ProductionOrder:
        self.session.add(production_order)
        await self.session.flush()
        await self.session.refresh(production_order)
        return production_order
