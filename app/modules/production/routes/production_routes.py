from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.services.stock_service import StockService
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import MealPlanRead
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.production.repositories.production_material_consumption_repository import (
    ProductionMaterialConsumptionRepository,
)
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.production.schemas.production_schema import (
    ProductionCostSheetRead,
    ProductionOrderBundleRead,
    ProductionOrderComplete,
    ProductionOrderRead,
)
from app.modules.production.services.production_service import ProductionService
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_production_service(session: AsyncSession = Depends(get_db_session)) -> ProductionService:
    meal_plan_service = MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
        InventoryBalanceRepository(session),
        WarehouseRepository(session),
    )
    stock_service = StockService(
        InventoryTransactionRepository(session),
        InventoryBalanceRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        ProductRepository(session),
        UomRepository(session),
        WarehouseRepository(session),
    )
    return ProductionService(
        ProductionOrderRepository(session),
        ProductionMaterialConsumptionRepository(session),
        meal_plan_service,
        InventoryBalanceRepository(session),
        ProductRepository(session),
        stock_service,
    )


@router.get("/")
async def list_production_orders(request: Request, service: ProductionService = Depends(get_production_service)) -> dict:
    items = [ProductionOrderRead.model_validate(item) for item in await service.list_production_orders()]
    return success_response(
        code="PRODUCTION_ORDER_LIST_FOUND",
        message="Daftar production order berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{production_order_id}")
async def get_production_order(
    production_order_id: UUID,
    request: Request,
    service: ProductionService = Depends(get_production_service),
) -> dict:
    payload = await service.get_production_order_bundle(production_order_id)
    return success_response(
        code="PRODUCTION_ORDER_FOUND",
        message="Detail production order berhasil diambil.",
        data=ProductionOrderBundleRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.post("/from-meal-plan/{meal_plan_id}", status_code=status.HTTP_201_CREATED)
async def create_production_order_from_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_production_service(session)
    payload = await service.create_from_meal_plan(meal_plan_id)
    await session.commit()
    return success_response(
        code="PRODUCTION_ORDER_CREATED",
        message="Production order berhasil dibuat dari meal plan.",
        data=ProductionOrderBundleRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{production_order_id}/complete")
async def complete_production_order(
    production_order_id: UUID,
    payload: ProductionOrderComplete,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_production_service(session)
    result = await service.complete_production_order(production_order_id, payload, current_user)
    await session.commit()
    return success_response(
        code="PRODUCTION_ORDER_COMPLETED",
        message="Production order berhasil diselesaikan.",
        data=ProductionOrderBundleRead.model_validate(result),
        meta={"request_id": request.state.request_id, "total": len(result["materials"])},
    )


@router.get("/{production_order_id}/cost-sheet")
async def get_cost_sheet(
    production_order_id: UUID,
    request: Request,
    service: ProductionService = Depends(get_production_service),
) -> dict:
    sheet = await service.get_cost_sheet(production_order_id)
    return success_response(
        code="PRODUCTION_COST_SHEET_FOUND",
        message="Cost sheet production order berhasil diambil.",
        data=ProductionCostSheetRead.model_validate(sheet),
        meta={"request_id": request.state.request_id, "total": len(sheet["materials"])},
    )
