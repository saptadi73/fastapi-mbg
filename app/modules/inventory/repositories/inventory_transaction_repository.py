from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.inventory_transaction import InventoryTransaction


class InventoryTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> list[InventoryTransaction]:
        query = select(InventoryTransaction).order_by(InventoryTransaction.transaction_at.desc())
        if tenant_id is not None:
            query = query.where(InventoryTransaction.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(InventoryTransaction.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction
