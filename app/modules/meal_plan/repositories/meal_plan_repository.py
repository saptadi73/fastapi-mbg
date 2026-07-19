from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.meal_plan.models.meal_plan import MealPlan


class MealPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[MealPlan]:
        result = await self.session.execute(select(MealPlan).order_by(MealPlan.plan_date.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, meal_plan_id: UUID) -> MealPlan | None:
        return await self.session.get(MealPlan, meal_plan_id)

    async def add(self, meal_plan: MealPlan) -> MealPlan:
        self.session.add(meal_plan)
        await self.session.flush()
        await self.session.refresh(meal_plan)
        return meal_plan
