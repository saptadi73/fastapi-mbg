from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.goods_receipt import GoodsReceipt


class GoodsReceiptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> list[GoodsReceipt]:
        query = select(GoodsReceipt).order_by(GoodsReceipt.created_at.desc())
        if tenant_id is not None:
            query = query.where(GoodsReceipt.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(GoodsReceipt.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, goods_receipt_id: UUID) -> GoodsReceipt | None:
        return await self.session.get(GoodsReceipt, goods_receipt_id)

    async def get_by_id_and_scope(
        self,
        goods_receipt_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> GoodsReceipt | None:
        query = select(GoodsReceipt).where(GoodsReceipt.id == goods_receipt_id)
        if tenant_id is not None:
            query = query.where(GoodsReceipt.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(GoodsReceipt.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(GoodsReceipt.id)).where(GoodsReceipt.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, goods_receipt: GoodsReceipt) -> GoodsReceipt:
        self.session.add(goods_receipt)
        await self.session.flush()
        await self.session.refresh(goods_receipt)
        return goods_receipt
