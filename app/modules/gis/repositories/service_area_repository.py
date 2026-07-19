from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.gis.models.service_area import ServiceArea


class ServiceAreaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[ServiceArea]:
        query = select(ServiceArea).order_by(ServiceArea.name)
        if tenant_id is not None:
            query = query.where(ServiceArea.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(ServiceArea.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, service_area_id: UUID) -> ServiceArea | None:
        return await self.session.get(ServiceArea, service_area_id)

    async def get_by_id_and_scope(
        self,
        service_area_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> ServiceArea | None:
        query = select(ServiceArea).where(ServiceArea.id == service_area_id)
        if tenant_id is not None:
            query = query.where(ServiceArea.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(ServiceArea.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, service_area: ServiceArea) -> ServiceArea:
        self.session.add(service_area)
        await self.session.flush()
        await self.session.refresh(service_area)
        return service_area
