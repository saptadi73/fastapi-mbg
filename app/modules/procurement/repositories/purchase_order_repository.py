from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.purchase_order import PurchaseOrder


class PurchaseOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[PurchaseOrder]:
        query = select(PurchaseOrder).order_by(PurchaseOrder.created_at.desc())
        if tenant_id is not None:
            query = query.where(PurchaseOrder.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(PurchaseOrder.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, purchase_order_id: UUID) -> PurchaseOrder | None:
        return await self.session.get(PurchaseOrder, purchase_order_id)

    async def get_by_id_and_scope(self, purchase_order_id: UUID, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> PurchaseOrder | None:
        query = select(PurchaseOrder).where(PurchaseOrder.id == purchase_order_id)
        if tenant_id is not None:
            query = query.where(PurchaseOrder.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(PurchaseOrder.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        self.session.add(purchase_order)
        await self.session.flush()
        await self.session.refresh(purchase_order)
        return purchase_order
