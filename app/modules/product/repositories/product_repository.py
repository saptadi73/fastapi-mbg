from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Product]:
        result = await self.session.execute(select(Product).order_by(Product.name))
        return list(result.scalars().all())

    async def get_by_id(self, product_id: UUID) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.tenant_id == tenant_id, Product.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product
