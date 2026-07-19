from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.meal_plan.models.meal_plan import MealPlan


class MealPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[MealPlan]:
        query = select(MealPlan).order_by(MealPlan.plan_date.desc())
        if tenant_id is not None:
            query = query.where(MealPlan.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(MealPlan.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, meal_plan_id: UUID) -> MealPlan | None:
        return await self.session.get(MealPlan, meal_plan_id)

    async def get_by_id_and_scope(
        self,
        meal_plan_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> MealPlan | None:
        query = select(MealPlan).where(MealPlan.id == meal_plan_id)
        if tenant_id is not None:
            query = query.where(MealPlan.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(MealPlan.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, meal_plan: MealPlan) -> MealPlan:
        self.session.add(meal_plan)
        await self.session.flush()
        await self.session.refresh(meal_plan)
        return meal_plan
