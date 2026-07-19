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
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.procurement.repositories.goods_receipt_line_repository import GoodsReceiptLineRepository
from app.modules.procurement.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.procurement.repositories.purchase_request_line_repository import PurchaseRequestLineRepository
from app.modules.procurement.repositories.purchase_request_repository import PurchaseRequestRepository
from app.modules.procurement.schemas.purchase_request_schema import GoodsReceiptCreateFromPurchaseRequest
from app.modules.procurement.services.procurement_service import ProcurementService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter(prefix="/purchase-requests")


def get_procurement_service(session: AsyncSession = Depends(get_db_session)) -> ProcurementService:
    stock_service = StockService(
        InventoryTransactionRepository(session),
        InventoryBalanceRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        ProductRepository(session),
        UomRepository(session),
        WarehouseRepository(session),
    )
    meal_plan_service = MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
        InventoryBalanceRepository(session),
        None,
    )
    return ProcurementService(
        PurchaseRequestRepository(session),
        PurchaseRequestLineRepository(session),
        GoodsReceiptRepository(session),
        GoodsReceiptLineRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        meal_plan_service,
        InventoryBalanceRepository(session),
        ProductRepository(session),
        stock_service,
    )


@router.get("/")
async def list_purchase_requests(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_purchase_requests()
    return success_response(
        code="PURCHASE_REQUEST_LIST_FOUND",
        message="Daftar purchase request berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{purchase_request_id}")
async def get_purchase_request(
    purchase_request_id: UUID,
    request: Request,
    service: ProcurementService = Depends(get_procurement_service),
) -> dict:
    payload = await service.get_purchase_request(purchase_request_id)
    return success_response(
        code="PURCHASE_REQUEST_FOUND",
        message="Detail purchase request berhasil diambil.",
        data=payload,
        meta={"request_id": request.state.request_id},
    )


@router.post("/from-meal-plan/{meal_plan_id}", status_code=status.HTTP_201_CREATED)
async def create_purchase_request_from_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "procurement_officer")),
) -> dict:
    service = get_procurement_service(session)
    payload = await service.create_purchase_request_from_meal_plan(meal_plan_id)
    await session.commit()
    return success_response(
        code="PURCHASE_REQUEST_CREATED",
        message="Purchase request berhasil dibuat dari meal plan.",
        data=payload,
        meta={"request_id": request.state.request_id, "total": len(payload["lines"])},
    )


@router.get("/goods-receipts/")
async def list_goods_receipts(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_goods_receipts()
    return success_response(
        code="GOODS_RECEIPT_LIST_FOUND",
        message="Daftar goods receipt berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/goods-receipts/{goods_receipt_id}")
async def get_goods_receipt(
    goods_receipt_id: UUID,
    request: Request,
    service: ProcurementService = Depends(get_procurement_service),
) -> dict:
    payload = await service.get_goods_receipt(goods_receipt_id)
    return success_response(
        code="GOODS_RECEIPT_FOUND",
        message="Detail goods receipt berhasil diambil.",
        data=payload,
        meta={"request_id": request.state.request_id},
    )


@router.post("/goods-receipts/from-purchase-request/{purchase_request_id}", status_code=status.HTTP_201_CREATED)
async def create_goods_receipt_from_purchase_request(
    purchase_request_id: UUID,
    payload: GoodsReceiptCreateFromPurchaseRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "procurement_officer")),
) -> dict:
    service = get_procurement_service(session)
    bundle = await service.create_goods_receipt_from_purchase_request(purchase_request_id, payload, current_user)
    await session.commit()
    return success_response(
        code="GOODS_RECEIPT_CREATED",
        message="Goods receipt berhasil dibuat dan inventory diposting.",
        data=bundle,
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )
