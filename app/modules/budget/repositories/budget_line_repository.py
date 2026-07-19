from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.budget.models.budget_line import BudgetLine


class BudgetLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_budget(self, budget_id: UUID) -> list[BudgetLine]:
        result = await self.session.execute(select(BudgetLine).where(BudgetLine.budget_id == budget_id).order_by(BudgetLine.created_at))
        return list(result.scalars().all())

    async def add(self, budget_line: BudgetLine) -> BudgetLine:
        self.session.add(budget_line)
        await self.session.flush()
        await self.session.refresh(budget_line)
        return budget_line

    async def list_by_budget_and_account(self, budget_id: UUID, account_id: UUID) -> list[BudgetLine]:
        result = await self.session.execute(
            select(BudgetLine)
            .where(BudgetLine.budget_id == budget_id, BudgetLine.account_id == account_id)
            .order_by(BudgetLine.created_at)
        )
        return list(result.scalars().all())
