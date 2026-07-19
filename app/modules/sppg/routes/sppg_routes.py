from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.sppg.schemas.sppg_schema import SppgCreate, SppgRead
from app.modules.sppg.services.sppg_service import SppgService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_sppg_service(session: AsyncSession = Depends(get_db_session)) -> SppgService:
    return SppgService(SppgRepository(session), TenantRepository(session))


@router.get("/")
async def list_sppg(
    request: Request,
    service: SppgService = Depends(get_sppg_service),
) -> dict:
    items = [SppgRead.model_validate(item) for item in await service.list_sppg()]
    return success_response(
        code="SPPG_LIST_FOUND",
        message="Daftar SPPG berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{sppg_id}")
async def get_sppg(
    sppg_id: UUID,
    request: Request,
    service: SppgService = Depends(get_sppg_service),
) -> dict:
    sppg = await service.get_sppg(sppg_id)
    return success_response(
        code="SPPG_FOUND",
        message="Detail SPPG berhasil diambil.",
        data=SppgRead.model_validate(sppg),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sppg(
    payload: SppgCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = SppgService(SppgRepository(session), TenantRepository(session))
    sppg = await service.create_sppg(payload)
    await session.commit()
    return success_response(
        code="SPPG_CREATED",
        message="SPPG berhasil dibuat.",
        data=SppgRead.model_validate(sppg),
        meta={"request_id": request.state.request_id},
    )
