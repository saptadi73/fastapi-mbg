from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.tenant.schemas.tenant_schema import TenantCreate, TenantRead
from app.modules.tenant.services.tenant_service import TenantService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_tenant_service(session: AsyncSession = Depends(get_db_session)) -> TenantService:
    return TenantService(TenantRepository(session))


@router.get("/")
async def list_tenants(
    request: Request,
    service: TenantService = Depends(get_tenant_service),
) -> dict:
    items = [TenantRead.model_validate(item) for item in await service.list_tenants()]
    return success_response(
        code="TENANT_LIST_FOUND",
        message="Daftar tenant berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: UUID,
    request: Request,
    service: TenantService = Depends(get_tenant_service),
) -> dict:
    tenant = await service.get_tenant(tenant_id)
    return success_response(
        code="TENANT_FOUND",
        message="Detail tenant berhasil diambil.",
        data=TenantRead.model_validate(tenant),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = TenantService(TenantRepository(session))
    tenant = await service.create_tenant(payload)
    await session.commit()
    return success_response(
        code="TENANT_CREATED",
        message="Tenant berhasil dibuat.",
        data=TenantRead.model_validate(tenant),
        meta={"request_id": request.state.request_id},
    )
