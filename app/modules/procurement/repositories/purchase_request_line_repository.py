from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.purchase_request_line import PurchaseRequestLine


class PurchaseRequestLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_purchase_request(self, purchase_request_id: UUID) -> list[PurchaseRequestLine]:
        result = await self.session.execute(
            select(PurchaseRequestLine)
            .where(PurchaseRequestLine.purchase_request_id == purchase_request_id)
            .order_by(PurchaseRequestLine.product_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, purchase_request_line_id: UUID) -> PurchaseRequestLine | None:
        return await self.session.get(PurchaseRequestLine, purchase_request_line_id)

    async def add(self, line: PurchaseRequestLine) -> PurchaseRequestLine:
        self.session.add(line)
        await self.session.flush()
        await self.session.refresh(line)
        return line
