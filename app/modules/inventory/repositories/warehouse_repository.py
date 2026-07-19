from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Warehouse]:
        query = select(Warehouse).order_by(Warehouse.name)
        if tenant_id is not None:
            query = query.where(Warehouse.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Warehouse.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, warehouse_id: UUID) -> Warehouse | None:
        return await self.session.get(Warehouse, warehouse_id)

    async def get_by_id_and_scope(
        self,
        warehouse_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> Warehouse | None:
        query = select(Warehouse).where(Warehouse.id == warehouse_id)
        if tenant_id is not None:
            query = query.where(Warehouse.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Warehouse.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Warehouse | None:
        result = await self.session.execute(
            select(Warehouse).where(Warehouse.tenant_id == tenant_id, Warehouse.code == code)
        )
        return result.scalar_one_or_none()

    async def list_by_sppg(self, sppg_id: UUID) -> list[Warehouse]:
        result = await self.session.execute(select(Warehouse).where(Warehouse.sppg_id == sppg_id).order_by(Warehouse.name))
        return list(result.scalars().all())

    async def add(self, warehouse: Warehouse) -> Warehouse:
        self.session.add(warehouse)
        await self.session.flush()
        await self.session.refresh(warehouse)
        return warehouse
