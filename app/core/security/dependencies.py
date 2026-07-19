from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.jwt import decode_token
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.support.exceptions.base import UnauthorizedException

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
        user_id = UUID(subject)
    except (ValueError, JWTError) as exc:
        raise UnauthorizedException(
            code="INVALID_ACCESS_TOKEN",
            message="Access token tidak valid.",
        ) from exc

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException(
            code="USER_NOT_FOUND",
            message="User tidak ditemukan atau tidak aktif.",
        )
    return user
