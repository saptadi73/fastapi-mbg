from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.purchase_request import PurchaseRequest


class PurchaseRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[PurchaseRequest]:
        result = await self.session.execute(select(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, purchase_request_id: UUID) -> PurchaseRequest | None:
        return await self.session.get(PurchaseRequest, purchase_request_id)

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(PurchaseRequest.id)).where(PurchaseRequest.tenant_id == tenant_id)
        )
        return int(result.scalar_one())

    async def add(self, purchase_request: PurchaseRequest) -> PurchaseRequest:
        self.session.add(purchase_request)
        await self.session.flush()
        await self.session.refresh(purchase_request)
        return purchase_request
