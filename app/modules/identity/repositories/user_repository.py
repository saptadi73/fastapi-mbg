from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.user import User
from app.modules.identity.models.user_sppg_access import UserSppgAccess


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def list_all(self, tenant_id: UUID | None = None) -> list[User]:
        query = select(User).order_by(User.full_name)
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id_and_tenant(self, user_id: UUID, tenant_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_accessible_sppg_ids(self, user_id: UUID) -> list[UUID]:
        result = await self.session.execute(
            select(UserSppgAccess.sppg_id).where(UserSppgAccess.user_id == user_id)
        )
        return list(result.scalars().all())

    async def add_sppg_access(self, user_id: UUID, tenant_id: UUID, sppg_id: UUID) -> None:
        result = await self.session.execute(
            select(UserSppgAccess).where(
                UserSppgAccess.user_id == user_id,
                UserSppgAccess.sppg_id == sppg_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return
        self.session.add(
            UserSppgAccess(
                user_id=user_id,
                tenant_id=tenant_id,
                sppg_id=sppg_id,
            )
        )
        await self.session.flush()

    async def remove_sppg_access_not_in(self, user_id: UUID, keep_sppg_ids: list[UUID]) -> None:
        query = delete(UserSppgAccess).where(UserSppgAccess.user_id == user_id)
        if keep_sppg_ids:
            query = query.where(UserSppgAccess.sppg_id.not_in(keep_sppg_ids))
        await self.session.execute(query)

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
