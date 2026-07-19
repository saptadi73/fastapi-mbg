from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.geography.schemas.school_schema import SchoolCreate, SchoolRead
from app.modules.geography.services.school_service import SchoolService
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_school_service(session: AsyncSession = Depends(get_db_session)) -> SchoolService:
    return SchoolService(SchoolRepository(session), TenantRepository(session))


@router.get("/")
async def list_schools(
    request: Request,
    service: SchoolService = Depends(get_school_service),
) -> dict:
    items = [SchoolRead.model_validate(item) for item in await service.list_schools()]
    return success_response(
        code="SCHOOL_LIST_FOUND",
        message="Daftar sekolah berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{school_id}")
async def get_school(
    school_id: UUID,
    request: Request,
    service: SchoolService = Depends(get_school_service),
) -> dict:
    school = await service.get_school(school_id)
    return success_response(
        code="SCHOOL_FOUND",
        message="Detail sekolah berhasil diambil.",
        data=SchoolRead.model_validate(school),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: SchoolCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = SchoolService(SchoolRepository(session), TenantRepository(session))
    school = await service.create_school(payload)
    await session.commit()
    return success_response(
        code="SCHOOL_CREATED",
        message="Sekolah berhasil dibuat.",
        data=SchoolRead.model_validate(school),
        meta={"request_id": request.state.request_id},
    )
