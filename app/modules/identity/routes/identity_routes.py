from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user as get_authenticated_user
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.user_schema import CurrentUserRead
from app.modules.identity.services.identity_service import IdentityService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_identity_service(session: AsyncSession = Depends(get_db_session)) -> IdentityService:
    return IdentityService(UserRepository(session))


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
