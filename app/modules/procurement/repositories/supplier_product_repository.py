from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier_product import SupplierProduct


class SupplierProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, supplier_id: UUID | None = None) -> list[SupplierProduct]:
        query = select(SupplierProduct).order_by(SupplierProduct.created_at.desc())
        if tenant_id is not None:
            query = query.where(SupplierProduct.tenant_id == tenant_id)
        if supplier_id is not None:
            query = query.where(SupplierProduct.supplier_id == supplier_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, supplier_product_id: UUID) -> SupplierProduct | None:
        return await self.session.get(SupplierProduct, supplier_product_id)

    async def get_by_scope(self, tenant_id: UUID, supplier_id: UUID, product_id: UUID) -> SupplierProduct | None:
        result = await self.session.execute(
            select(SupplierProduct).where(
                SupplierProduct.tenant_id == tenant_id,
                SupplierProduct.supplier_id == supplier_id,
                SupplierProduct.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def add(self, supplier_product: SupplierProduct) -> SupplierProduct:
        self.session.add(supplier_product)
        await self.session.flush()
        await self.session.refresh(supplier_product)
        return supplier_product
