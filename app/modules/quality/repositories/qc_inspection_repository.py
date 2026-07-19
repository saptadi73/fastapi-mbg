from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.quality.models.qc_inspection import QCInspection
from app.modules.quality.models.qc_inspection_line import QCInspectionLine


class QCInspectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[QCInspection]:
        query = select(QCInspection).order_by(QCInspection.inspection_at.desc(), QCInspection.created_at.desc())
        if tenant_id is not None:
            query = query.where(QCInspection.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(QCInspection.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, inspection_id: UUID) -> QCInspection | None:
        return await self.session.get(QCInspection, inspection_id)

    async def get_by_id_and_scope(
        self,
        inspection_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> QCInspection | None:
        query = select(QCInspection).where(QCInspection.id == inspection_id)
        if tenant_id is not None:
            query = query.where(QCInspection.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(QCInspection.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            select(QCInspection.id).where(QCInspection.tenant_id == tenant_id)
        )
        return len(list(result.scalars().all()))

    async def add(self, inspection: QCInspection) -> QCInspection:
        self.session.add(inspection)
        await self.session.flush()
        await self.session.refresh(inspection)
        return inspection

    async def list_lines(self, inspection_id: UUID) -> list[QCInspectionLine]:
        result = await self.session.execute(
            select(QCInspectionLine).where(QCInspectionLine.inspection_id == inspection_id).order_by(QCInspectionLine.created_at)
        )
        return list(result.scalars().all())

    async def add_line(self, line: QCInspectionLine) -> QCInspectionLine:
        self.session.add(line)
        await self.session.flush()
        await self.session.refresh(line)
        return line

    async def list_mandatory_by_reference(self, reference_type: str, reference_id: UUID) -> list[QCInspection]:
        result = await self.session.execute(
            select(QCInspection).where(
                QCInspection.reference_type == reference_type,
                QCInspection.reference_id == reference_id,
                QCInspection.is_mandatory_for_release.is_(True),
            )
        )
        return list(result.scalars().all())
