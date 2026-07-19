from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.delivery.repositories.delivery_incident_repository import DeliveryIncidentRepository
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.delivery.repositories.delivery_proof_repository import DeliveryProofRepository
from app.modules.delivery.repositories.delivery_route_repository import DeliveryRouteRepository
from app.modules.delivery.repositories.delivery_route_stop_repository import DeliveryRouteStopRepository
from app.modules.delivery.schemas.delivery_schema import (
    DeliveryCreateFromProduction,
    DeliveryIncidentCreate,
    DeliveryIncidentRead,
    DeliveryOrderBundleRead,
    DeliveryOrderRead,
    DeliveryProofCreate,
    DeliveryRouteBundleRead,
    DeliveryRouteCreate,
    DeliveryRouteRead,
)
from app.modules.delivery.services.delivery_service import DeliveryService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.stock_location_repository import StockLocationRepository
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
from app.modules.quality.repositories.qc_inspection_repository import QCInspectionRepository
from app.modules.quality.services.quality_service import QualityService
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
        StockLocationRepository(session),
        InventoryBatchRepository(session),
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
        DeliveryRouteRepository(session),
        DeliveryRouteStopRepository(session),
        DeliveryIncidentRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        SchoolRepository(session),
        production_service,
        QualityService(
            QCInspectionRepository(session),
            TenantRepository(session),
            SppgRepository(session),
            ProductionOrderRepository(session),
        ),
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


@router.get("/routes")
async def list_delivery_routes(request: Request, service: DeliveryService = Depends(get_delivery_service)) -> dict:
    items = [DeliveryRouteRead.model_validate(item) for item in await service.list_routes()]
    return success_response(
        code="DELIVERY_ROUTE_LIST_FOUND",
        message="Daftar route delivery berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/routes/{route_id}")
async def get_delivery_route(
    route_id: UUID,
    request: Request,
    service: DeliveryService = Depends(get_delivery_service),
) -> dict:
    payload = await service.get_route(route_id)
    return success_response(
        code="DELIVERY_ROUTE_FOUND",
        message="Detail route delivery berhasil diambil.",
        data=DeliveryRouteBundleRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
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


@router.post("/routes", status_code=status.HTTP_201_CREATED)
async def create_delivery_route(
    payload: DeliveryRouteCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "delivery_officer")),
) -> dict:
    service = get_delivery_service(session)
    result = await service.create_route(payload)
    await session.commit()
    return success_response(
        code="DELIVERY_ROUTE_CREATED",
        message="Route delivery berhasil dibuat.",
        data=DeliveryRouteBundleRead.model_validate(result),
        meta={"request_id": request.state.request_id, "total": len(result["stops"])},
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


@router.post("/{delivery_order_id}/incidents", status_code=status.HTTP_201_CREATED)
async def record_delivery_incident(
    delivery_order_id: UUID,
    payload: DeliveryIncidentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "delivery_officer")),
) -> dict:
    service = get_delivery_service(session)
    result = await service.record_incident(delivery_order_id, payload)
    await session.commit()
    return success_response(
        code="DELIVERY_INCIDENT_RECORDED",
        message="Incident delivery berhasil dicatat.",
        data={
            "incident": DeliveryIncidentRead.model_validate(result["incident"]),
            "delivery": DeliveryOrderBundleRead.model_validate(result["delivery"]),
        },
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
