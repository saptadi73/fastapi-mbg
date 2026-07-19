from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.purchase_request import PurchaseRequest


class PurchaseRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> list[PurchaseRequest]:
        query = select(PurchaseRequest).order_by(PurchaseRequest.created_at.desc())
        if tenant_id is not None:
            query = query.where(PurchaseRequest.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(PurchaseRequest.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, purchase_request_id: UUID) -> PurchaseRequest | None:
        return await self.session.get(PurchaseRequest, purchase_request_id)

    async def get_by_id_and_scope(
        self,
        purchase_request_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> PurchaseRequest | None:
        query = select(PurchaseRequest).where(PurchaseRequest.id == purchase_request_id)
        if tenant_id is not None:
            query = query.where(PurchaseRequest.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(PurchaseRequest.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

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
