from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import (
    MealPlanCostPreviewRead,
    MealPlanCreate,
    MealPlanMaterialReservationRead,
    MealPlanRead,
)
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_meal_plan_service(session: AsyncSession = Depends(get_db_session)) -> MealPlanService:
    return MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
        InventoryBalanceRepository(session),
        WarehouseRepository(session),
    )


@router.get("/")
async def list_meal_plans(request: Request, service: MealPlanService = Depends(get_meal_plan_service)) -> dict:
    items = [MealPlanRead.model_validate(item) for item in await service.list_meal_plans()]
    return success_response(
        code="MEAL_PLAN_LIST_FOUND",
        message="Daftar meal plan berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{meal_plan_id}")
async def get_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
) -> dict:
    meal_plan = await service.get_meal_plan(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_FOUND",
        message="Detail meal plan berhasil diambil.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    payload: MealPlanCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
    )
    meal_plan = await service.create_meal_plan(payload)
    await session.commit()
    return success_response(
        code="MEAL_PLAN_CREATED",
        message="Meal plan berhasil dibuat.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/calculate-requirements")
async def calculate_requirements(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    requirements = await service.calculate_material_requirements(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_REQUIREMENTS_CALCULATED",
        message="Kebutuhan bahan berhasil dihitung.",
        data=requirements,
        meta={"request_id": request.state.request_id, "total": len(requirements)},
    )


@router.post("/{meal_plan_id}/submit")
async def submit_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    meal_plan = await service.submit_meal_plan(meal_plan_id)
    await session.commit()
    return success_response(
        code="MEAL_PLAN_SUBMITTED",
        message="Meal plan berhasil disubmit.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/approve")
async def approve_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    meal_plan = await service.approve_meal_plan(meal_plan_id)
    await session.commit()
    return success_response(
        code="MEAL_PLAN_APPROVED",
        message="Meal plan berhasil diapprove.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/reserve-materials")
async def reserve_materials(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    reservation = await service.reserve_materials(meal_plan_id)
    await session.commit()
    return success_response(
        code="MEAL_PLAN_MATERIALS_RESERVED",
        message="Material meal plan berhasil direservasi.",
        data=MealPlanMaterialReservationRead.model_validate(reservation),
        meta={"request_id": request.state.request_id, "total": len(reservation["reserved_items"])},
    )


@router.get("/{meal_plan_id}/cost-preview")
async def get_cost_preview(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
) -> dict:
    preview = await service.get_cost_preview(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_COST_PREVIEW_FOUND",
        message="Preview biaya meal plan berhasil diambil.",
        data=MealPlanCostPreviewRead.model_validate(preview),
        meta={"request_id": request.state.request_id, "total": len(preview["line_items"])},
    )
