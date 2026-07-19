from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.production.models.production_material_consumption import ProductionMaterialConsumption


class ProductionMaterialConsumptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_production_order(self, production_order_id: UUID) -> list[ProductionMaterialConsumption]:
        result = await self.session.execute(
            select(ProductionMaterialConsumption)
            .where(ProductionMaterialConsumption.production_order_id == production_order_id)
            .order_by(ProductionMaterialConsumption.product_id)
        )
        return list(result.scalars().all())

    async def add(self, item: ProductionMaterialConsumption) -> ProductionMaterialConsumption:
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item
