from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.delivery.repositories.delivery_proof_repository import DeliveryProofRepository
from app.modules.delivery.schemas.delivery_schema import (
    DeliveryCreateFromProduction,
    DeliveryOrderBundleRead,
    DeliveryOrderRead,
    DeliveryProofCreate,
)
from app.modules.delivery.services.delivery_service import DeliveryService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.services.stock_service import StockService
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.production.repositories.production_material_consumption_repository import (
    ProductionMaterialConsumptionRepository,
)
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.production.services.production_service import ProductionService
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_delivery_service(session: AsyncSession = Depends(get_db_session)) -> DeliveryService:
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
    production_service = ProductionService(
        ProductionOrderRepository(session),
        ProductionMaterialConsumptionRepository(session),
        meal_plan_service,
        InventoryBalanceRepository(session),
        ProductRepository(session),
        stock_service,
    )
    return DeliveryService(
        DeliveryOrderRepository(session),
        DeliveryProofRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        SchoolRepository(session),
        production_service,
    )


@router.get("/")
async def list_delivery_orders(request: Request, service: DeliveryService = Depends(get_delivery_service)) -> dict:
    items = [DeliveryOrderRead.model_validate(item) for item in await service.list_delivery_orders()]
    return success_response(
        code="DELIVERY_ORDER_LIST_FOUND",
        message="Daftar delivery order berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{delivery_order_id}")
async def get_delivery_order(
    delivery_order_id: UUID,
    request: Request,
    service: DeliveryService = Depends(get_delivery_service),
) -> dict:
    payload = await service.get_delivery_order(delivery_order_id)
    return success_response(
        code="DELIVERY_ORDER_FOUND",
        message="Detail delivery order berhasil diambil.",
        data=DeliveryOrderBundleRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.post("/from-production-order/{production_order_id}", status_code=status.HTTP_201_CREATED)
async def create_delivery_order_from_production_order(
    production_order_id: UUID,
    payload: DeliveryCreateFromProduction,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "delivery_officer")),
) -> dict:
    service = get_delivery_service(session)
    result = await service.create_from_production_order(production_order_id, payload)
    await session.commit()
    return success_response(
        code="DELIVERY_ORDER_CREATED",
        message="Delivery order berhasil dibuat dari production order.",
        data=DeliveryOrderBundleRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{delivery_order_id}/proof", status_code=status.HTTP_201_CREATED)
async def record_delivery_proof(
    delivery_order_id: UUID,
    payload: DeliveryProofCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "delivery_officer")),
) -> dict:
    service = get_delivery_service(session)
    result = await service.record_proof(delivery_order_id, payload)
    await session.commit()
    return success_response(
        code="DELIVERY_PROOF_RECORDED",
        message="Proof of delivery berhasil dicatat.",
        data=DeliveryOrderBundleRead.model_validate(result),
        meta={"request_id": request.state.request_id, "total": len(result["proofs"])},
    )
