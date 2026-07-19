from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.program.repositories.program_repository import ProgramRepository
from app.modules.program.schemas.program_schema import (
    ProgramBundleRead,
    ProgramCreate,
    ProgramPeriodCreate,
    ProgramPeriodRead,
    ProgramRead,
    ProgramSppgAssignmentCreate,
    ProgramSppgAssignmentRead,
    ProgramTenantAssignmentCreate,
    ProgramTenantAssignmentRead,
)
from app.modules.program.services.program_service import ProgramService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter(prefix="/programs")


def get_program_service(session: AsyncSession = Depends(get_db_session)) -> ProgramService:
    return ProgramService(
        ProgramRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


@router.get("/")
async def list_programs(
    request: Request,
    service: ProgramService = Depends(get_program_service),
) -> dict:
    items = [ProgramRead.model_validate(item) for item in await service.list_programs()]
    return success_response(
        code="PROGRAM_LIST_FOUND",
        message="Daftar program berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{program_id}")
async def get_program(
    program_id: UUID,
    request: Request,
    service: ProgramService = Depends(get_program_service),
) -> dict:
    bundle = await service.get_program_bundle(program_id)
    return success_response(
        code="PROGRAM_FOUND",
        message="Detail program berhasil diambil.",
        data=ProgramBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: ProgramCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_program_service(session)
    program = await service.create_program(payload)
    await session.commit()
    return success_response(
        code="PROGRAM_CREATED",
        message="Program berhasil dibuat.",
        data=ProgramRead.model_validate(program),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{program_id}/periods", status_code=status.HTTP_201_CREATED)
async def create_program_period(
    program_id: UUID,
    payload: ProgramPeriodCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_program_service(session)
    period = await service.create_program_period(program_id, payload)
    await session.commit()
    return success_response(
        code="PROGRAM_PERIOD_CREATED",
        message="Periode program berhasil dibuat.",
        data=ProgramPeriodRead.model_validate(period),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{program_id}/tenants", status_code=status.HTTP_201_CREATED)
async def assign_tenant_to_program(
    program_id: UUID,
    payload: ProgramTenantAssignmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_program_service(session)
    assignment = await service.assign_tenant(program_id, payload)
    await session.commit()
    return success_response(
        code="PROGRAM_TENANT_ASSIGNED",
        message="Tenant berhasil diassign ke program.",
        data=ProgramTenantAssignmentRead.model_validate(assignment),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{program_id}/sppg", status_code=status.HTTP_201_CREATED)
async def assign_sppg_to_program(
    program_id: UUID,
    payload: ProgramSppgAssignmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_program_service(session)
    assignment = await service.assign_sppg(program_id, payload)
    await session.commit()
    return success_response(
        code="PROGRAM_SPPG_ASSIGNED",
        message="SPPG berhasil diassign ke program.",
        data=ProgramSppgAssignmentRead.model_validate(assignment),
        meta={"request_id": request.state.request_id},
    )
