from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None) -> list[Supplier]:
        query = select(Supplier).order_by(Supplier.name)
        if tenant_id is not None:
            query = query.where(Supplier.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        return await self.session.get(Supplier, supplier_id)

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Supplier | None:
        result = await self.session.execute(select(Supplier).where(Supplier.tenant_id == tenant_id, Supplier.code == code))
        return result.scalar_one_or_none()

    async def add(self, supplier: Supplier) -> Supplier:
        self.session.add(supplier)
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier
