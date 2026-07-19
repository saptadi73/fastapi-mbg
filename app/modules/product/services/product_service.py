from uuid import UUID

from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.product.models.product import Product
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.product.schemas.product_schema import ProductCreate
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.exceptions.base import ConflictException, NotFoundException


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        tenant_repository: TenantRepository,
        uom_repository: UomRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.uom_repository = uom_repository

    async def list_products(self) -> list[Product]:
        return await self.repository.list_all()

    async def get_product(self, product_id: UUID) -> Product:
        product = await self.repository.get_by_id(product_id)
        if product is None:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk tidak ditemukan.")
        return product

    async def create_product(self, payload: ProductCreate) -> Product:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        stock_uom_id = UUID(payload.stock_uom_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk produk tidak ditemukan.")
        uom = await self.uom_repository.get_by_id(stock_uom_id)
        if uom is None or uom.tenant_id != tenant_id:
            raise NotFoundException(code="UOM_NOT_FOUND", message="Stock UoM produk tidak ditemukan.")
        existing = await self.repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(code="PRODUCT_CODE_ALREADY_EXISTS", message="Kode produk sudah digunakan pada tenant ini.")
        product = Product(
            tenant_id=tenant_id,
            code=payload.code,
            name=payload.name,
            product_type=payload.product_type,
            stock_uom_id=stock_uom_id,
            standard_cost=payload.standard_cost,
            track_batch=payload.track_batch,
            track_expiry=payload.track_expiry,
            minimum_stock=payload.minimum_stock,
            maximum_stock=payload.maximum_stock,
            reorder_point=payload.reorder_point,
            valuation_method=payload.valuation_method,
            is_active=payload.is_active,
        )
        return await self.repository.add(product)
