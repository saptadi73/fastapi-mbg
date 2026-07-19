from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.user_schema import TokenRead
from app.support.exceptions.base import NotFoundException


class IdentityService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def authenticate(self, email: str, password: str) -> TokenRead:
        user = await self.repository.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise NotFoundException(
                code="INVALID_CREDENTIALS",
                message="Email atau password tidak valid.",
            )

        token = create_access_token(
            subject=str(user.id),
            claims={
                "tenant_id": str(user.tenant_id),
                "active_sppg_id": str(user.active_sppg_id) if user.active_sppg_id else None,
                "roles": user.role_names,
                "email": user.email,
            },
        )
        return TokenRead(access_token=token, active_sppg_id=user.active_sppg_id)

    async def get_current_user(self, user: User) -> User:
        return user
