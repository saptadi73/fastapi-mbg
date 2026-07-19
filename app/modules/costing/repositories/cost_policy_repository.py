from datetime import date
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.costing.models.cost_policy import CostPolicy


class CostPolicyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[CostPolicy]:
        query = select(CostPolicy).order_by(CostPolicy.effective_from.desc(), CostPolicy.name)
        if tenant_id is not None:
            query = query.where(CostPolicy.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(or_(CostPolicy.sppg_id == sppg_id, CostPolicy.sppg_id.is_(None)))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, policy_id: UUID) -> CostPolicy | None:
        return await self.session.get(CostPolicy, policy_id)

    async def get_by_tenant_code(self, tenant_id: UUID, code: str) -> CostPolicy | None:
        result = await self.session.execute(
            select(CostPolicy).where(CostPolicy.tenant_id == tenant_id, CostPolicy.code == code)
        )
        return result.scalar_one_or_none()

    async def add(self, policy: CostPolicy) -> CostPolicy:
        self.session.add(policy)
        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def get_active_policy_for_date(self, tenant_id: UUID, sppg_id: UUID | None, target_date: date) -> CostPolicy | None:
        query = (
            select(CostPolicy)
            .where(
                CostPolicy.tenant_id == tenant_id,
                CostPolicy.is_active.is_(True),
                CostPolicy.effective_from <= target_date,
                or_(CostPolicy.effective_to.is_(None), CostPolicy.effective_to >= target_date),
            )
            .order_by(CostPolicy.sppg_id.is_(None), CostPolicy.effective_from.desc())
        )
        if sppg_id is not None:
            query = query.where(or_(CostPolicy.sppg_id == sppg_id, CostPolicy.sppg_id.is_(None)))
        result = await self.session.execute(query)
        return result.scalars().first()
