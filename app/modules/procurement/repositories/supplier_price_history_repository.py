from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier_price_history import SupplierPriceHistory


class SupplierPriceHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, supplier_product_id: UUID | None = None) -> list[SupplierPriceHistory]:
        query = select(SupplierPriceHistory).order_by(desc(SupplierPriceHistory.effective_from), SupplierPriceHistory.created_at.desc())
        if tenant_id is not None:
            query = query.where(SupplierPriceHistory.tenant_id == tenant_id)
        if supplier_product_id is not None:
            query = query.where(SupplierPriceHistory.supplier_product_id == supplier_product_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add(self, history: SupplierPriceHistory) -> SupplierPriceHistory:
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history

    async def get_latest_for_supplier_product(self, supplier_product_id: UUID) -> SupplierPriceHistory | None:
        result = await self.session.execute(
            select(SupplierPriceHistory)
            .where(SupplierPriceHistory.supplier_product_id == supplier_product_id)
            .order_by(desc(SupplierPriceHistory.effective_from), SupplierPriceHistory.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
