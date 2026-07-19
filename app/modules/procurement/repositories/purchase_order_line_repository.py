from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.purchase_order_line import PurchaseOrderLine


class PurchaseOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_purchase_order(self, purchase_order_id: UUID) -> list[PurchaseOrderLine]:
        result = await self.session.execute(
            select(PurchaseOrderLine)
            .where(PurchaseOrderLine.purchase_order_id == purchase_order_id)
            .order_by(PurchaseOrderLine.created_at.asc())
        )
        return list(result.scalars().all())

    async def add(self, purchase_order_line: PurchaseOrderLine) -> PurchaseOrderLine:
        self.session.add(purchase_order_line)
        await self.session.flush()
        await self.session.refresh(purchase_order_line)
        return purchase_order_line
