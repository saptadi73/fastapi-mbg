from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.product.schemas.product_schema import ProductCreate, ProductRead
from app.modules.product.services.product_service import ProductService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_product_service(session: AsyncSession = Depends(get_db_session)) -> ProductService:
    return ProductService(ProductRepository(session), TenantRepository(session), UomRepository(session))


@router.get("/")
async def list_products(request: Request, service: ProductService = Depends(get_product_service)) -> dict:
    items = [ProductRead.model_validate(item) for item in await service.list_products()]
    return success_response(
        code="PRODUCT_LIST_FOUND",
        message="Daftar produk berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{product_id}")
async def get_product(product_id: UUID, request: Request, service: ProductService = Depends(get_product_service)) -> dict:
    product = await service.get_product(product_id)
    return success_response(
        code="PRODUCT_FOUND",
        message="Detail produk berhasil diambil.",
        data=ProductRead.model_validate(product),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = ProductService(ProductRepository(session), TenantRepository(session), UomRepository(session))
    product = await service.create_product(payload)
    await session.commit()
    return success_response(
        code="PRODUCT_CREATED",
        message="Produk berhasil dibuat.",
        data=ProductRead.model_validate(product),
        meta={"request_id": request.state.request_id},
    )
