from uuid import UUID

from app.core.security.jwt import create_access_token
from app.core.security.password import verify_password
from app.core.security.password import hash_password
from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.user_schema import (
    ActiveSppgSwitchRequest,
    CurrentUserRead,
    TokenRead,
    UserAdminRead,
    UserCreate,
    UserSppgAccessRead,
    UserSppgAccessUpdate,
    UserUpdate,
)
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class IdentityService:
    def __init__(
        self,
        repository: UserRepository,
        sppg_repository: SppgRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.repository = repository
        self.sppg_repository = sppg_repository
        self.tenant_repository = tenant_repository

    def _get_tenant_scope(self) -> UUID | None:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            return None
        try:
            return UUID(current_tenant)
        except ValueError as exc:
            raise BadRequestException(
                code="INVALID_TENANT_CONTEXT",
                message="Header X-Tenant-ID tidak valid.",
            ) from exc

    async def _build_user_admin_read(self, user: User) -> dict:
        accessible_sppg_ids = await self.repository.list_accessible_sppg_ids(user.id)
        return UserAdminRead(
            id=user.id,
            tenant_id=user.tenant_id,
            active_sppg_id=user.active_sppg_id,
            accessible_sppg_ids=accessible_sppg_ids,
            full_name=user.full_name,
            email=user.email,
            role_names=user.role_names,
            is_active=user.is_active,
        ).model_dump()

    async def switch_active_sppg(self, user: User, payload: ActiveSppgSwitchRequest) -> dict:
        accessible_sppg_ids = await self.repository.list_accessible_sppg_ids(user.id)
        target_sppg_id = UUID(payload.sppg_id)
        if target_sppg_id not in accessible_sppg_ids:
            raise BadRequestException(
                code="ACTIVE_SPPG_NOT_ACCESSIBLE",
                message="SPPG yang dipilih tidak termasuk akses user.",
            )
        sppg = await self.sppg_repository.get_by_id(target_sppg_id)
        if sppg is None or sppg.tenant_id != user.tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG tidak ditemukan.")
        user.active_sppg_id = target_sppg_id
        token = create_access_token(
            subject=str(user.id),
            claims={
                "tenant_id": str(user.tenant_id),
                "active_sppg_id": str(user.active_sppg_id),
                "accessible_sppg_ids": [str(sppg_id) for sppg_id in accessible_sppg_ids],
                "roles": user.role_names,
                "email": user.email,
            },
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "active_sppg_id": user.active_sppg_id,
            "accessible_sppg_ids": accessible_sppg_ids,
        }

    async def authenticate(self, email: str, password: str) -> TokenRead:
        user = await self.repository.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise NotFoundException(
                code="INVALID_CREDENTIALS",
                message="Email atau password tidak valid.",
            )

        accessible_sppg_ids = await self.repository.list_accessible_sppg_ids(user.id)
        token = create_access_token(
            subject=str(user.id),
            claims={
                "tenant_id": str(user.tenant_id),
                "active_sppg_id": str(user.active_sppg_id) if user.active_sppg_id else None,
                "accessible_sppg_ids": [str(sppg_id) for sppg_id in accessible_sppg_ids],
                "roles": user.role_names,
                "email": user.email,
            },
        )
        return TokenRead(
            access_token=token,
            active_sppg_id=user.active_sppg_id,
            accessible_sppg_ids=accessible_sppg_ids,
        )

    async def get_current_user(self, user: User) -> dict:
        accessible_sppg_ids = await self.repository.list_accessible_sppg_ids(user.id)
        return CurrentUserRead(
            id=user.id,
            tenant_id=user.tenant_id,
            active_sppg_id=user.active_sppg_id,
            accessible_sppg_ids=accessible_sppg_ids,
            full_name=user.full_name,
            email=user.email,
            role_names=user.role_names,
        ).model_dump()

    async def list_users(self) -> list[dict]:
        tenant_scope = self._get_tenant_scope()
        users = await self.repository.list_all(tenant_scope)
        items: list[dict] = []
        for user in users:
            items.append(await self._build_user_admin_read(user))
        return items

    async def get_user_admin(self, user_id: UUID) -> dict:
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is None:
            user = await self.repository.get_by_id(user_id)
        else:
            user = await self.repository.get_by_id_and_tenant(user_id, tenant_scope)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User tidak ditemukan atau tidak aktif.")
        return await self._build_user_admin_read(user)

    async def create_user(self, payload: UserCreate) -> dict:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk user tidak ditemukan.")
        if await self.repository.get_by_email(str(payload.email)) is not None:
            raise ConflictException(code="USER_EMAIL_ALREADY_EXISTS", message="Email user sudah digunakan.")
        accessible_sppg_ids = [UUID(sppg_id) for sppg_id in payload.accessible_sppg_ids]
        for sppg_id in accessible_sppg_ids:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG akses user tidak ditemukan.")
        active_sppg_id = UUID(payload.active_sppg_id) if payload.active_sppg_id else None
        if active_sppg_id is not None and active_sppg_id not in accessible_sppg_ids:
            raise BadRequestException(
                code="ACTIVE_SPPG_NOT_IN_ACCESS_LIST",
                message="active_sppg_id harus termasuk dalam accessible_sppg_ids.",
            )
        user = await self.repository.add(
            User(
                tenant_id=tenant_id,
                active_sppg_id=active_sppg_id,
                full_name=payload.full_name,
                email=str(payload.email),
                password_hash=hash_password(payload.password),
                is_active=payload.is_active,
                role_names=payload.role_names,
            )
        )
        for sppg_id in accessible_sppg_ids:
            await self.repository.add_sppg_access(user.id, tenant_id, sppg_id)
        return await self._build_user_admin_read(user)

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> dict:
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is None:
            user = await self.repository.get_by_id(user_id)
        else:
            user = await self.repository.get_by_id_and_tenant(user_id, tenant_scope)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User tidak ditemukan atau tidak aktif.")
        accessible_sppg_ids = [UUID(sppg_id) for sppg_id in payload.accessible_sppg_ids]
        for sppg_id in accessible_sppg_ids:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != user.tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG akses user tidak ditemukan.")
        active_sppg_id = UUID(payload.active_sppg_id) if payload.active_sppg_id else None
        if active_sppg_id is not None and active_sppg_id not in accessible_sppg_ids:
            raise BadRequestException(
                code="ACTIVE_SPPG_NOT_IN_ACCESS_LIST",
                message="active_sppg_id harus termasuk dalam accessible_sppg_ids.",
            )
        user.full_name = payload.full_name
        user.role_names = payload.role_names
        user.is_active = payload.is_active
        if payload.password:
            user.password_hash = hash_password(payload.password)
        await self.repository.remove_sppg_access_not_in(user.id, accessible_sppg_ids)
        for sppg_id in accessible_sppg_ids:
            await self.repository.add_sppg_access(user.id, user.tenant_id, sppg_id)
        user.active_sppg_id = active_sppg_id
        return await self._build_user_admin_read(user)

    async def get_user_sppg_access(self, user_id: UUID) -> dict:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User tidak ditemukan atau tidak aktif.")
        accessible_sppg_ids = await self.repository.list_accessible_sppg_ids(user.id)
        return UserSppgAccessRead(
            user_id=user.id,
            tenant_id=user.tenant_id,
            active_sppg_id=user.active_sppg_id,
            accessible_sppg_ids=accessible_sppg_ids,
        ).model_dump()

    async def update_user_sppg_access(self, user_id: UUID, payload: UserSppgAccessUpdate) -> dict:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User tidak ditemukan atau tidak aktif.")

        accessible_sppg_ids = [UUID(sppg_id) for sppg_id in payload.accessible_sppg_ids]
        for sppg_id in accessible_sppg_ids:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != user.tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG akses user tidak ditemukan.")

        active_sppg_id = UUID(payload.active_sppg_id) if payload.active_sppg_id else None
        if active_sppg_id is not None and active_sppg_id not in accessible_sppg_ids:
            raise BadRequestException(
                code="ACTIVE_SPPG_NOT_IN_ACCESS_LIST",
                message="active_sppg_id harus termasuk dalam accessible_sppg_ids.",
            )

        await self.repository.remove_sppg_access_not_in(user.id, accessible_sppg_ids)
        for sppg_id in accessible_sppg_ids:
            await self.repository.add_sppg_access(user.id, user.tenant_id, sppg_id)

        user.active_sppg_id = active_sppg_id
        refreshed_access = await self.repository.list_accessible_sppg_ids(user.id)
        return UserSppgAccessRead(
            user_id=user.id,
            tenant_id=user.tenant_id,
            active_sppg_id=user.active_sppg_id,
            accessible_sppg_ids=refreshed_access,
        ).model_dump()
