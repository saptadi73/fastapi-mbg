from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sppg.models.sppg import Sppg


class SppgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None) -> list[Sppg]:
        query = select(Sppg).order_by(Sppg.name)
        if tenant_id is not None:
            query = query.where(Sppg.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, sppg_id: UUID) -> Sppg | None:
        return await self.session.get(Sppg, sppg_id)

    async def get_by_id_and_tenant(self, sppg_id: UUID, tenant_id: UUID) -> Sppg | None:
        result = await self.session.execute(
            select(Sppg).where(Sppg.id == sppg_id, Sppg.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Sppg | None:
        result = await self.session.execute(
            select(Sppg).where(Sppg.tenant_id == tenant_id, Sppg.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, sppg: Sppg) -> Sppg:
        self.session.add(sppg)
        await self.session.flush()
        await self.session.refresh(sppg)
        return sppg
