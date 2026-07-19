from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.uom.models.uom import Uom


class UomRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Uom]:
        result = await self.session.execute(select(Uom).order_by(Uom.name))
        return list(result.scalars().all())

    async def get_by_id(self, uom_id: UUID) -> Uom | None:
        return await self.session.get(Uom, uom_id)

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Uom | None:
        result = await self.session.execute(
            select(Uom).where(Uom.tenant_id == tenant_id, Uom.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, uom: Uom) -> Uom:
        self.session.add(uom)
        await self.session.flush()
        await self.session.refresh(uom)
        return uom
