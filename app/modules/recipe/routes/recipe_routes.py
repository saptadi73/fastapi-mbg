from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.recipe.schemas.recipe_schema import (
    RecipeCreate,
    RecipeLineCreate,
    RecipeLineRead,
    RecipeRead,
)
from app.modules.recipe.services.recipe_service import RecipeService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_recipe_service(session: AsyncSession = Depends(get_db_session)) -> RecipeService:
    return RecipeService(
        RecipeRepository(session),
        RecipeLineRepository(session),
        TenantRepository(session),
        ProductRepository(session),
        UomRepository(session),
    )


@router.get("/")
async def list_recipes(request: Request, service: RecipeService = Depends(get_recipe_service)) -> dict:
    items = [RecipeRead.model_validate(item) for item in await service.list_recipes()]
    return success_response(
        code="RECIPE_LIST_FOUND",
        message="Daftar recipe berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: UUID, request: Request, service: RecipeService = Depends(get_recipe_service)) -> dict:
    recipe = await service.get_recipe(recipe_id)
    return success_response(
        code="RECIPE_FOUND",
        message="Detail recipe berhasil diambil.",
        data=RecipeRead.model_validate(recipe),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = RecipeService(
        RecipeRepository(session),
        RecipeLineRepository(session),
        TenantRepository(session),
        ProductRepository(session),
        UomRepository(session),
    )
    recipe = await service.create_recipe(payload)
    await session.commit()
    return success_response(
        code="RECIPE_CREATED",
        message="Recipe berhasil dibuat.",
        data=RecipeRead.model_validate(recipe),
        meta={"request_id": request.state.request_id},
    )


@router.get("/{recipe_id}/lines")
async def list_recipe_lines(
    recipe_id: UUID,
    request: Request,
    service: RecipeService = Depends(get_recipe_service),
) -> dict:
    items = [RecipeLineRead.model_validate(item) for item in await service.list_recipe_lines(recipe_id)]
    return success_response(
        code="RECIPE_LINE_LIST_FOUND",
        message="Daftar recipe line berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/{recipe_id}/lines", status_code=status.HTTP_201_CREATED)
async def create_recipe_line(
    recipe_id: UUID,
    payload: RecipeLineCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = RecipeService(
        RecipeRepository(session),
        RecipeLineRepository(session),
        TenantRepository(session),
        ProductRepository(session),
        UomRepository(session),
    )
    recipe_line = await service.create_recipe_line(recipe_id, payload)
    await session.commit()
    return success_response(
        code="RECIPE_LINE_CREATED",
        message="Recipe line berhasil dibuat.",
        data=RecipeLineRead.model_validate(recipe_line),
        meta={"request_id": request.state.request_id},
    )
