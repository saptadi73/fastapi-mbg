from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.geography.models.school import School


class SchoolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None) -> list[School]:
        query = select(School).order_by(School.name)
        if tenant_id is not None:
            query = query.where(School.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, school_id: UUID) -> School | None:
        return await self.session.get(School, school_id)

    async def get_by_id_and_tenant(self, school_id: UUID, tenant_id: UUID) -> School | None:
        result = await self.session.execute(
            select(School).where(School.id == school_id, School.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> School | None:
        result = await self.session.execute(
            select(School).where(School.tenant_id == tenant_id, School.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, school: School) -> School:
        self.session.add(school)
        await self.session.flush()
        await self.session.refresh(school)
        return school
