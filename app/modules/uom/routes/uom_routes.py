from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.modules.uom.schemas.uom_schema import UomCreate, UomRead
from app.modules.uom.services.uom_service import UomService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_uom_service(session: AsyncSession = Depends(get_db_session)) -> UomService:
    return UomService(UomRepository(session), TenantRepository(session))


@router.get("/")
async def list_uoms(request: Request, service: UomService = Depends(get_uom_service)) -> dict:
    items = [UomRead.model_validate(item) for item in await service.list_uoms()]
    return success_response(
        code="UOM_LIST_FOUND",
        message="Daftar UoM berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{uom_id}")
async def get_uom(uom_id: UUID, request: Request, service: UomService = Depends(get_uom_service)) -> dict:
    uom = await service.get_uom(uom_id)
    return success_response(
        code="UOM_FOUND",
        message="Detail UoM berhasil diambil.",
        data=UomRead.model_validate(uom),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_uom(
    payload: UomCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = UomService(UomRepository(session), TenantRepository(session))
    uom = await service.create_uom(payload)
    await session.commit()
    return success_response(
        code="UOM_CREATED",
        message="UoM berhasil dibuat.",
        data=UomRead.model_validate(uom),
        meta={"request_id": request.state.request_id},
    )
