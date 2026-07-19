from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.budget.models.budget import Budget


class BudgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None) -> list[Budget]:
        query = select(Budget).order_by(Budget.created_at.desc())
        if tenant_id is not None:
            query = query.where(Budget.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, budget_id: UUID) -> Budget | None:
        return await self.session.get(Budget, budget_id)

    async def get_by_id_and_tenant(self, budget_id: UUID, tenant_id: UUID) -> Budget | None:
        result = await self.session.execute(
            select(Budget).where(Budget.id == budget_id, Budget.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(Budget.id)).where(Budget.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, budget: Budget) -> Budget:
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget)
        return budget

    async def list_approved_by_tenant_and_date(self, tenant_id: UUID, on_date: date) -> list[Budget]:
        result = await self.session.execute(
            select(Budget).where(
                Budget.tenant_id == tenant_id,
                Budget.status == "APPROVED",
                Budget.date_start <= on_date,
                Budget.date_end >= on_date,
            )
        )
        return list(result.scalars().all())
