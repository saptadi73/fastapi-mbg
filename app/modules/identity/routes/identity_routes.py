from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user as get_authenticated_user
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
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


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: IdentityService = Depends(get_identity_service),
) -> dict:
    token = await service.authenticate(form_data.username, form_data.password)
    await get_audit_service(service.repository.session).record_event(
        event_type="SECURITY",
        module_name="identity",
        action_name="LOGIN",
        summary="User berhasil login.",
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"email": form_data.username},
    )
    await service.repository.session.commit()
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
    await get_audit_service(session).record_event(
        event_type="ACCESS",
        module_name="identity",
        action_name="SWITCH_ACTIVE_SPPG",
        summary="User mengganti SPPG aktif.",
        actor=authenticated_user,
        tenant_id=authenticated_user.tenant_id,
        sppg_id=authenticated_user.active_sppg_id,
        entity_type="user",
        entity_id=authenticated_user.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"target_sppg_id": payload.sppg_id},
    )
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
    actor: User = Depends(get_authenticated_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.create_user(payload)
    await get_audit_service(session).record_event(
        event_type="MASTER_DATA",
        module_name="identity",
        action_name="CREATE_USER",
        summary="User baru dibuat.",
        actor=actor,
        tenant_id=UUID(payload.tenant_id),
        entity_type="user",
        entity_id=UUID(str(result["id"])),
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"email": str(payload.email), "role_names": payload.role_names},
    )
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
    actor: User = Depends(get_authenticated_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.update_user(user_id, payload)
    await get_audit_service(session).record_event(
        event_type="PERMISSION",
        module_name="identity",
        action_name="UPDATE_USER",
        summary="User diperbarui.",
        actor=actor,
        tenant_id=UUID(str(result["tenant_id"])),
        entity_type="user",
        entity_id=user_id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"role_names": payload.role_names, "is_active": payload.is_active},
    )
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
    actor: User = Depends(get_authenticated_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    service = get_identity_service(session)
    result = await service.update_user_sppg_access(user_id=user_id, payload=payload)
    await get_audit_service(session).record_event(
        event_type="PERMISSION",
        module_name="identity",
        action_name="UPDATE_USER_SPPG_ACCESS",
        summary="Akses SPPG user diperbarui.",
        actor=actor,
        tenant_id=UUID(str(result["tenant_id"])),
        sppg_id=UUID(payload.active_sppg_id) if payload.active_sppg_id else None,
        entity_type="user",
        entity_id=user_id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"accessible_sppg_ids": payload.accessible_sppg_ids},
    )
    await session.commit()
    return success_response(
        code="IDENTITY_USER_SPPG_ACCESS_UPDATED",
        message="Akses SPPG user berhasil diperbarui.",
        data=UserSppgAccessRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )
