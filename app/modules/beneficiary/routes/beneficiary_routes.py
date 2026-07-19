from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.beneficiary.repositories.beneficiary_repository import BeneficiaryRepository
from app.modules.beneficiary.schemas.beneficiary_schema import BeneficiaryCreate, BeneficiaryRead
from app.modules.beneficiary.services.beneficiary_service import BeneficiaryService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_beneficiary_service(session: AsyncSession = Depends(get_db_session)) -> BeneficiaryService:
    return BeneficiaryService(
        BeneficiaryRepository(session),
        TenantRepository(session),
        SchoolRepository(session),
    )


@router.get("/")
async def list_beneficiaries(
    request: Request,
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> dict:
    items = [BeneficiaryRead.model_validate(item) for item in await service.list_beneficiaries()]
    return success_response(
        code="BENEFICIARY_LIST_FOUND",
        message="Daftar beneficiary berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{beneficiary_id}")
async def get_beneficiary(
    beneficiary_id: UUID,
    request: Request,
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> dict:
    beneficiary = await service.get_beneficiary(beneficiary_id)
    return success_response(
        code="BENEFICIARY_FOUND",
        message="Detail beneficiary berhasil diambil.",
        data=BeneficiaryRead.model_validate(beneficiary),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    payload: BeneficiaryCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = BeneficiaryService(
        BeneficiaryRepository(session),
        TenantRepository(session),
        SchoolRepository(session),
    )
    beneficiary = await service.create_beneficiary(payload)
    await session.commit()
    return success_response(
        code="BENEFICIARY_CREATED",
        message="Beneficiary berhasil dibuat.",
        data=BeneficiaryRead.model_validate(beneficiary),
        meta={"request_id": request.state.request_id},
    )
