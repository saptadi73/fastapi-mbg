from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.stock_location import StockLocation


class StockLocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
        warehouse_id: UUID | None = None,
    ) -> list[StockLocation]:
        query = select(StockLocation).order_by(StockLocation.name)
        if tenant_id is not None:
            query = query.where(StockLocation.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(StockLocation.sppg_id == sppg_id)
        if warehouse_id is not None:
            query = query.where(StockLocation.warehouse_id == warehouse_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, location_id: UUID) -> StockLocation | None:
        return await self.session.get(StockLocation, location_id)

    async def get_by_tenant_warehouse_code(self, tenant_id: UUID, warehouse_id: UUID, code: str) -> StockLocation | None:
        result = await self.session.execute(
            select(StockLocation).where(
                StockLocation.tenant_id == tenant_id,
                StockLocation.warehouse_id == warehouse_id,
                StockLocation.code == code,
            )
        )
        return result.scalar_one_or_none()

    async def get_root_by_warehouse(self, warehouse_id: UUID) -> StockLocation | None:
        result = await self.session.execute(
            select(StockLocation)
            .where(StockLocation.warehouse_id == warehouse_id, StockLocation.parent_id.is_(None))
            .order_by(StockLocation.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def add(self, location: StockLocation) -> StockLocation:
        self.session.add(location)
        await self.session.flush()
        await self.session.refresh(location)
        return location
