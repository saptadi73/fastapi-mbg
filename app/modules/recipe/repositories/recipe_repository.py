from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.models.recipe import Recipe


class RecipeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Recipe]:
        result = await self.session.execute(select(Recipe).order_by(Recipe.name))
        return list(result.scalars().all())

    async def get_by_id(self, recipe_id: UUID) -> Recipe | None:
        return await self.session.get(Recipe, recipe_id)

    async def get_by_tenant_code_version(self, tenant_id: UUID, code: str, version: int) -> Recipe | None:
        result = await self.session.execute(
            select(Recipe).where(
                Recipe.tenant_id == tenant_id,
                Recipe.code == code,
                Recipe.version == version,
            )
        )
        return result.scalar_one_or_none()

    async def add(self, recipe: Recipe) -> Recipe:
        self.session.add(recipe)
        await self.session.flush()
        await self.session.refresh(recipe)
        return recipe
