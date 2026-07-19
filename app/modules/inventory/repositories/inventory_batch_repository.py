from datetime import date
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.inventory_batch import InventoryBatch


class InventoryBatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        product_id: UUID | None = None,
        warehouse_id: UUID | None = None,
    ) -> list[InventoryBatch]:
        query = select(InventoryBatch).order_by(asc(InventoryBatch.expiry_date), InventoryBatch.batch_number)
        if tenant_id is not None:
            query = query.where(InventoryBatch.tenant_id == tenant_id)
        if product_id is not None:
            query = query.where(InventoryBatch.product_id == product_id)
        if warehouse_id is not None:
            query = query.where(InventoryBatch.warehouse_id == warehouse_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, batch_id: UUID) -> InventoryBatch | None:
        return await self.session.get(InventoryBatch, batch_id)

    async def get_by_scope(self, tenant_id: UUID, product_id: UUID, batch_number: str) -> InventoryBatch | None:
        result = await self.session.execute(
            select(InventoryBatch).where(
                InventoryBatch.tenant_id == tenant_id,
                InventoryBatch.product_id == product_id,
                InventoryBatch.batch_number == batch_number,
            )
        )
        return result.scalar_one_or_none()

    async def list_fefo_candidates(self, tenant_id: UUID, product_id: UUID, warehouse_id: UUID | None = None) -> list[InventoryBatch]:
        query = (
            select(InventoryBatch)
            .where(
                InventoryBatch.tenant_id == tenant_id,
                InventoryBatch.product_id == product_id,
                InventoryBatch.is_blocked.is_(False),
                InventoryBatch.quantity_available > 0,
            )
            .order_by(asc(InventoryBatch.expiry_date), asc(InventoryBatch.received_date), asc(InventoryBatch.batch_number))
        )
        if warehouse_id is not None:
            query = query.where(InventoryBatch.warehouse_id == warehouse_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_expiring(self, tenant_id: UUID, before_date: date) -> list[InventoryBatch]:
        result = await self.session.execute(
            select(InventoryBatch)
            .where(
                InventoryBatch.tenant_id == tenant_id,
                InventoryBatch.expiry_date.is_not(None),
                InventoryBatch.expiry_date <= before_date,
                InventoryBatch.quantity_available > 0,
            )
            .order_by(asc(InventoryBatch.expiry_date), asc(InventoryBatch.batch_number))
        )
        return list(result.scalars().all())

    async def add(self, batch: InventoryBatch) -> InventoryBatch:
        self.session.add(batch)
        await self.session.flush()
        await self.session.refresh(batch)
        return batch
