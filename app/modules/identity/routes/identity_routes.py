from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user as get_authenticated_user
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.user_schema import (
    ActiveSppgSwitchRequest,
    CurrentUserRead,
    UserAdminRead,
    UserCreate,
    UserSppgAccessRead,
    UserSppgAccessUpdate,
    UserUpdate,
)
from app.modules.identity.services.identity_service import IdentityService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_identity_service(session: AsyncSession = Depends(get_db_session)) -> IdentityService:
    return IdentityService(UserRepository(session), SppgRepository(session), TenantRepository(session))


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: IdentityService = Depends(get_identity_service),
) -> dict:
    token = await service.authenticate(form_data.username, form_data.password)
    return success_response(
        code="IDENTITY_LOGIN_SUCCESS",
        message="Login berhasil.",
        data=token,
        meta={"request_id": request.state.request_id},
    )


@router.get("/me")
async def get_current_user(
    request: Request,
    authenticated_user: User = Depends(get_authenticated_user),
    service: IdentityService = Depends(get_identity_service),
) -> dict:
    current_user = await service.get_current_user(authenticated_user)
    return success_response(
        code="IDENTITY_CURRENT_USER_FOUND",
        message="Profil user berhasil diambil.",
        data=CurrentUserRead.model_validate(current_user),
        meta={"request_id": request.state.request_id},
    )


@router.post("/switch-active-sppg")
async def switch_active_sppg(
    payload: ActiveSppgSwitchRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict:
    service = get_identity_service(session)
    result = await service.switch_active_sppg(authenticated_user, payload)
    await session.commit()
    return success_response(
        code="IDENTITY_ACTIVE_SPPG_SWITCHED",
        message="SPPG aktif berhasil diganti.",
        data=result,
        meta={"request_id": request.state.request_id},
    )


@router.get("/users/{user_id}/sppg-access")
async def get_user_sppg_access(
    user_id: UUID,
    request: Request,
    service: IdentityService = Depends(get_identity_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    payload = await service.get_user_sppg_access(user_id=user_id)
    return success_response(
        code="IDENTITY_USER_SPPG_ACCESS_FOUND",
        message="Akses SPPG user berhasil diambil.",
        data=UserSppgAccessRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/users")
async def list_users(
    request: Request,
    service: IdentityService = Depends(get_identity_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [UserAdminRead.model_validate(item) for item in await service.list_users()]
    return success_response(
        code="IDENTITY_USER_LIST_FOUND",
        message="Daftar user berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    request: Request,
    service: IdentityService = Depends(get_identity_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    payload = await service.get_user_admin(user_id)
    return success_response(
        code="IDENTITY_USER_FOUND",
        message="Detail user berhasil diambil.",
        data=UserAdminRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.post("/users")
async def create_user(
    payload: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.create_user(payload)
    await session.commit()
    return success_response(
        code="IDENTITY_USER_CREATED",
        message="User berhasil dibuat.",
        data=UserAdminRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )


@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.update_user(user_id, payload)
    await session.commit()
    return success_response(
        code="IDENTITY_USER_UPDATED",
        message="User berhasil diperbarui.",
        data=UserAdminRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )


@router.put("/users/{user_id}/sppg-access")
async def update_user_sppg_access(
    user_id: UUID,
    payload: UserSppgAccessUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.update_user_sppg_access(user_id=user_id, payload=payload)
    await session.commit()
    return success_response(
        code="IDENTITY_USER_SPPG_ACCESS_UPDATED",
        message="Akses SPPG user berhasil diperbarui.",
        data=UserSppgAccessRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )
