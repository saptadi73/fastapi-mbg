from uuid import UUID

from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.models.recipe import Recipe
from app.modules.recipe.models.recipe_line import RecipeLine
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.recipe.schemas.recipe_schema import RecipeCreate, RecipeLineCreate
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.exceptions.base import ConflictException, NotFoundException


class RecipeService:
    def __init__(
        self,
        repository: RecipeRepository,
        recipe_line_repository: RecipeLineRepository,
        tenant_repository: TenantRepository,
        product_repository: ProductRepository,
        uom_repository: UomRepository,
    ) -> None:
        self.repository = repository
        self.recipe_line_repository = recipe_line_repository
        self.tenant_repository = tenant_repository
        self.product_repository = product_repository
        self.uom_repository = uom_repository

    async def list_recipes(self) -> list[Recipe]:
        return await self.repository.list_all()

    async def get_recipe(self, recipe_id: UUID) -> Recipe:
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundException(code="RECIPE_NOT_FOUND", message="Recipe tidak ditemukan.")
        return recipe

    async def create_recipe(self, payload: RecipeCreate) -> Recipe:
        tenant_id = UUID(payload.tenant_id)
        product_id = UUID(payload.product_id)
        output_uom_id = UUID(payload.output_uom_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk recipe tidak ditemukan.")
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk recipe tidak ditemukan.")
        uom = await self.uom_repository.get_by_id(output_uom_id)
        if uom is None or uom.tenant_id != tenant_id:
            raise NotFoundException(code="UOM_NOT_FOUND", message="Output UoM recipe tidak ditemukan.")
        existing = await self.repository.get_by_tenant_code_version(tenant_id, payload.code, payload.version)
        if existing is not None:
            raise ConflictException(code="RECIPE_CODE_VERSION_ALREADY_EXISTS", message="Code dan versi recipe sudah digunakan.")
        recipe = Recipe(
            tenant_id=tenant_id,
            product_id=product_id,
            code=payload.code,
            name=payload.name,
            version=payload.version,
            output_quantity=payload.output_quantity,
            output_uom_id=output_uom_id,
            effective_from=payload.effective_from,
            status=payload.status,
            is_active=payload.is_active,
        )
        return await self.repository.add(recipe)

    async def list_recipe_lines(self, recipe_id: UUID) -> list[RecipeLine]:
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundException(code="RECIPE_NOT_FOUND", message="Recipe tidak ditemukan.")
        return await self.recipe_line_repository.list_by_recipe(recipe_id)

    async def create_recipe_line(self, recipe_id: UUID, payload: RecipeLineCreate) -> RecipeLine:
        tenant_id = UUID(payload.tenant_id)
        component_product_id = UUID(payload.component_product_id)
        uom_id = UUID(payload.uom_id)
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None or recipe.tenant_id != tenant_id:
            raise NotFoundException(code="RECIPE_NOT_FOUND", message="Recipe tidak ditemukan.")
        product = await self.product_repository.get_by_id(component_product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk bahan recipe tidak ditemukan.")
        uom = await self.uom_repository.get_by_id(uom_id)
        if uom is None or uom.tenant_id != tenant_id:
            raise NotFoundException(code="UOM_NOT_FOUND", message="UoM recipe line tidak ditemukan.")
        recipe_line = RecipeLine(
            tenant_id=tenant_id,
            recipe_id=recipe_id,
            component_product_id=component_product_id,
            quantity=payload.quantity,
            uom_id=uom_id,
            waste_percentage=payload.waste_percentage,
            sequence=payload.sequence,
        )
        return await self.recipe_line_repository.add(recipe_line)
