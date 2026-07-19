from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.models.recipe_line import RecipeLine


class RecipeLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_recipe(self, recipe_id: UUID) -> list[RecipeLine]:
        result = await self.session.execute(
            select(RecipeLine).where(RecipeLine.recipe_id == recipe_id).order_by(RecipeLine.sequence)
        )
        return list(result.scalars().all())

    async def add(self, recipe_line: RecipeLine) -> RecipeLine:
        self.session.add(recipe_line)
        await self.session.flush()
        await self.session.refresh(recipe_line)
        return recipe_line
