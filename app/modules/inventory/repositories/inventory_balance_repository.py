from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.inventory_balance import InventoryBalance


class InventoryBalanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[InventoryBalance]:
        result = await self.session.execute(
            select(InventoryBalance).order_by(InventoryBalance.warehouse_id, InventoryBalance.product_id)
        )
        return list(result.scalars().all())

    async def get_by_warehouse_and_product(self, warehouse_id: UUID, product_id: UUID) -> InventoryBalance | None:
        result = await self.session.execute(
            select(InventoryBalance).where(
                InventoryBalance.warehouse_id == warehouse_id,
                InventoryBalance.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_sppg_and_product(self, sppg_id: UUID, product_id: UUID) -> list[InventoryBalance]:
        result = await self.session.execute(
            select(InventoryBalance)
            .where(
                InventoryBalance.sppg_id == sppg_id,
                InventoryBalance.product_id == product_id,
            )
            .order_by(InventoryBalance.quantity_available.desc(), InventoryBalance.warehouse_id)
        )
        return list(result.scalars().all())

    async def add(self, balance: InventoryBalance) -> InventoryBalance:
        self.session.add(balance)
        await self.session.flush()
        await self.session.refresh(balance)
        return balance
