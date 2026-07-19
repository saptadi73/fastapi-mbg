from collections.abc import Callable

from fastapi import Depends

from app.core.security.dependencies import get_current_user
from app.modules.identity.models.user import User
from app.support.exceptions.base import ForbiddenException


def require_roles(*allowed_roles: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        user_roles = set(user.role_names)
        if not user_roles.intersection(allowed_roles):
            raise ForbiddenException(
                code="INSUFFICIENT_ROLE",
                message="Anda tidak memiliki role yang diperlukan untuk aksi ini.",
            )
        return user

    return dependency
