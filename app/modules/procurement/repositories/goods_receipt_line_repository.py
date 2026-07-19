from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.goods_receipt_line import GoodsReceiptLine


class GoodsReceiptLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_goods_receipt(self, goods_receipt_id: UUID) -> list[GoodsReceiptLine]:
        result = await self.session.execute(
            select(GoodsReceiptLine)
            .where(GoodsReceiptLine.goods_receipt_id == goods_receipt_id)
            .order_by(GoodsReceiptLine.product_id)
        )
        return list(result.scalars().all())

    async def add(self, line: GoodsReceiptLine) -> GoodsReceiptLine:
        self.session.add(line)
        await self.session.flush()
        await self.session.refresh(line)
        return line
