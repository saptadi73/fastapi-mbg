from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.inventory_transaction import InventoryTransaction


class InventoryTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[InventoryTransaction]:
        result = await self.session.execute(
            select(InventoryTransaction).order_by(InventoryTransaction.transaction_at.desc())
        )
        return list(result.scalars().all())

    async def add(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction
