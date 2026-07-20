from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.jwt import decode_token
from app.core.tenancy.context import get_current_sppg, get_current_tenant, set_current_sppg, set_current_tenant
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.support.exceptions.base import BadRequestException, ForbiddenException, UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/identity/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if not token:
        raise UnauthorizedException(
            code="AUTHENTICATION_REQUIRED",
            message="Bearer token wajib disertakan.",
        )

    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if not subject:
            raise ValueError("JWT subject is missing.")
        if get_current_tenant() is None and payload.get("tenant_id"):
            set_current_tenant(str(payload["tenant_id"]))
        if get_current_sppg() is None and payload.get("active_sppg_id"):
            set_current_sppg(str(payload["active_sppg_id"]))
        user_id = UUID(subject)
    except (ValueError, JWTError) as exc:
        raise UnauthorizedException(
            code="INVALID_ACCESS_TOKEN",
            message="Access token tidak valid.",
        ) from exc

    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException(
            code="USER_NOT_FOUND",
            message="User tidak ditemukan atau tidak aktif.",
        )
    accessible_sppg_ids = await repository.list_accessible_sppg_ids(user.id)
    current_sppg = get_current_sppg()
    if current_sppg is not None:
        try:
            current_sppg_id = UUID(current_sppg)
        except ValueError as exc:
            raise BadRequestException(
                code="INVALID_SPPG_CONTEXT",
                message="Header X-SPPG-ID tidak valid.",
            ) from exc
        if accessible_sppg_ids and current_sppg_id not in accessible_sppg_ids:
            raise ForbiddenException(
                code="USER_SPPG_ACCESS_DENIED",
                message="User tidak memiliki akses ke SPPG pada context ini.",
            )
    elif user.active_sppg_id is not None and accessible_sppg_ids and user.active_sppg_id not in accessible_sppg_ids:
        raise ForbiddenException(
            code="USER_SPPG_ACCESS_DENIED",
            message="User tidak memiliki akses ke active SPPG yang tersimpan.",
        )
    return user
