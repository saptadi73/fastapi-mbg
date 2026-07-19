from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.budget.repositories.budget_line_repository import BudgetLineRepository
from app.modules.budget.repositories.budget_repository import BudgetRepository
from app.modules.budget.services.budget_service import BudgetService
from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.stock_location_repository import StockLocationRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.services.stock_service import StockService
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.procurement.repositories.goods_receipt_line_repository import GoodsReceiptLineRepository
from app.modules.procurement.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.procurement.repositories.purchase_order_line_repository import PurchaseOrderLineRepository
from app.modules.procurement.repositories.purchase_order_repository import PurchaseOrderRepository
from app.modules.procurement.repositories.purchase_request_line_repository import PurchaseRequestLineRepository
from app.modules.procurement.repositories.purchase_request_repository import PurchaseRequestRepository
from app.modules.procurement.repositories.supplier_price_history_repository import SupplierPriceHistoryRepository
from app.modules.procurement.repositories.supplier_product_repository import SupplierProductRepository
from app.modules.procurement.repositories.supplier_repository import SupplierRepository
from app.modules.procurement.repositories.supplier_invoice_line_repository import SupplierInvoiceLineRepository
from app.modules.procurement.repositories.supplier_invoice_repository import SupplierInvoiceRepository
from app.modules.procurement.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.modules.procurement.schemas.purchase_request_schema import (
    GoodsReceiptCreateFromPurchaseOrder,
    GoodsReceiptCreateFromPurchaseRequest,
    PurchaseOrderCreateFromRequest,
    SupplierCreate,
    SupplierInvoiceCreateFromGoodsReceipt,
    SupplierPaymentCreateFromInvoice,
    SupplierPriceHistoryCreate,
    SupplierProductCreate,
)
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
    accounting_service = AccountingService(
        AccountRepository(session),
        JournalEntryRepository(session),
        JournalLineRepository(session),
        TenantRepository(session),
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
    budget_service = BudgetService(
        BudgetRepository(session),
        BudgetLineRepository(session),
        TenantRepository(session),
        AccountRepository(session),
    )
    return ProcurementService(
        PurchaseRequestRepository(session),
        PurchaseRequestLineRepository(session),
        PurchaseOrderRepository(session),
        PurchaseOrderLineRepository(session),
        GoodsReceiptRepository(session),
        GoodsReceiptLineRepository(session),
        SupplierRepository(session),
        SupplierProductRepository(session),
        SupplierPriceHistoryRepository(session),
        SupplierInvoiceRepository(session),
        SupplierInvoiceLineRepository(session),
        SupplierPaymentRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        meal_plan_service,
        InventoryBalanceRepository(session),
        InventoryBatchRepository(session),
        ProductRepository(session),
        stock_service,
        accounting_service,
        budget_service,
    )


@router.get("/suppliers")
async def list_suppliers(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_suppliers()
    return success_response(
        code="SUPPLIER_LIST_FOUND",
        message="Daftar supplier berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: UUID, request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    supplier = await service.get_supplier(supplier_id)
    return success_response(
        code="SUPPLIER_FOUND",
        message="Detail supplier berhasil diambil.",
        data=supplier,
        meta={"request_id": request.state.request_id},
    )


@router.post("/suppliers", status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "procurement_officer", "operations_manager")),
) -> dict:
    service = get_procurement_service(session)
    supplier = await service.create_supplier(payload)
    await session.commit()
    return success_response(
        code="SUPPLIER_CREATED",
        message="Supplier berhasil dibuat.",
        data=supplier,
        meta={"request_id": request.state.request_id},
    )


@router.get("/supplier-products")
async def list_supplier_products(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_supplier_products()
    return success_response(
        code="SUPPLIER_PRODUCT_LIST_FOUND",
        message="Daftar supplier product berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/supplier-products", status_code=status.HTTP_201_CREATED)
async def create_supplier_product(
    payload: SupplierProductCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "procurement_officer", "operations_manager")),
) -> dict:
    service = get_procurement_service(session)
    supplier_product = await service.create_supplier_product(payload)
    await session.commit()
    return success_response(
        code="SUPPLIER_PRODUCT_CREATED",
        message="Supplier product berhasil dibuat.",
        data=supplier_product,
        meta={"request_id": request.state.request_id},
    )


@router.get("/supplier-price-histories")
async def list_supplier_price_histories(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_supplier_price_histories()
    return success_response(
        code="SUPPLIER_PRICE_HISTORY_LIST_FOUND",
        message="Daftar histori harga supplier berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/supplier-price-histories", status_code=status.HTTP_201_CREATED)
async def create_supplier_price_history(
    payload: SupplierPriceHistoryCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "procurement_officer", "operations_manager")),
) -> dict:
    service = get_procurement_service(session)
    history = await service.create_supplier_price_history(payload)
    await session.commit()
    return success_response(
        code="SUPPLIER_PRICE_HISTORY_CREATED",
        message="Histori harga supplier berhasil dibuat.",
        data=history,
        meta={"request_id": request.state.request_id},
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


@router.get("/purchase-orders/")
async def list_purchase_orders(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_purchase_orders()
    return success_response(
        code="PURCHASE_ORDER_LIST_FOUND",
        message="Daftar purchase order berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/purchase-orders/{purchase_order_id}")
async def get_purchase_order(purchase_order_id: UUID, request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    payload = await service.get_purchase_order(purchase_order_id)
    return success_response(
        code="PURCHASE_ORDER_FOUND",
        message="Detail purchase order berhasil diambil.",
        data=payload,
        meta={"request_id": request.state.request_id},
    )


@router.post("/purchase-orders/from-purchase-request/{purchase_request_id}", status_code=status.HTTP_201_CREATED)
async def create_purchase_order_from_purchase_request(
    purchase_request_id: UUID,
    payload: PurchaseOrderCreateFromRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "procurement_officer", "operations_manager")),
) -> dict:
    service = get_procurement_service(session)
    bundle = await service.create_purchase_order_from_request(purchase_request_id, payload)
    await session.commit()
    return success_response(
        code="PURCHASE_ORDER_CREATED",
        message="Purchase order berhasil dibuat dari purchase request.",
        data=bundle,
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
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


@router.post("/goods-receipts/from-purchase-order/{purchase_order_id}", status_code=status.HTTP_201_CREATED)
async def create_goods_receipt_from_purchase_order(
    purchase_order_id: UUID,
    payload: GoodsReceiptCreateFromPurchaseOrder,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "procurement_officer")),
) -> dict:
    service = get_procurement_service(session)
    bundle = await service.create_goods_receipt_from_purchase_order(purchase_order_id, payload, current_user)
    await session.commit()
    return success_response(
        code="GOODS_RECEIPT_CREATED_FROM_PO",
        message="Goods receipt berhasil dibuat dari purchase order.",
        data=bundle,
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.get("/supplier-invoices/")
async def list_supplier_invoices(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_supplier_invoices()
    return success_response(
        code="SUPPLIER_INVOICE_LIST_FOUND",
        message="Daftar supplier invoice berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/supplier-invoices/{supplier_invoice_id}")
async def get_supplier_invoice(
    supplier_invoice_id: UUID,
    request: Request,
    service: ProcurementService = Depends(get_procurement_service),
) -> dict:
    payload = await service.get_supplier_invoice(supplier_invoice_id)
    return success_response(
        code="SUPPLIER_INVOICE_FOUND",
        message="Detail supplier invoice berhasil diambil.",
        data=payload,
        meta={"request_id": request.state.request_id},
    )


@router.post("/supplier-invoices/from-goods-receipt/{goods_receipt_id}", status_code=status.HTTP_201_CREATED)
async def create_supplier_invoice_from_goods_receipt(
    goods_receipt_id: UUID,
    payload: SupplierInvoiceCreateFromGoodsReceipt,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "procurement_officer", "finance_manager")),
) -> dict:
    service = get_procurement_service(session)
    bundle = await service.create_supplier_invoice_from_goods_receipt(goods_receipt_id, payload, current_user)
    await session.commit()
    return success_response(
        code="SUPPLIER_INVOICE_CREATED",
        message="Supplier invoice berhasil dibuat, budget diaktualkan, dan hutang diposting.",
        data=bundle,
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.get("/supplier-payments/")
async def list_supplier_payments(request: Request, service: ProcurementService = Depends(get_procurement_service)) -> dict:
    items = await service.list_supplier_payments()
    return success_response(
        code="SUPPLIER_PAYMENT_LIST_FOUND",
        message="Daftar supplier payment berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/supplier-payments/{supplier_payment_id}")
async def get_supplier_payment(
    supplier_payment_id: UUID,
    request: Request,
    service: ProcurementService = Depends(get_procurement_service),
) -> dict:
    payload = await service.get_supplier_payment(supplier_payment_id)
    return success_response(
        code="SUPPLIER_PAYMENT_FOUND",
        message="Detail supplier payment berhasil diambil.",
        data=payload,
        meta={"request_id": request.state.request_id},
    )


@router.post("/supplier-payments/from-supplier-invoice/{supplier_invoice_id}", status_code=status.HTTP_201_CREATED)
async def create_supplier_payment_from_supplier_invoice(
    supplier_invoice_id: UUID,
    payload: SupplierPaymentCreateFromInvoice,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_procurement_service(session)
    payment = await service.create_supplier_payment_from_invoice(supplier_invoice_id, payload, current_user)
    await session.commit()
    return success_response(
        code="SUPPLIER_PAYMENT_CREATED",
        message="Supplier payment berhasil dibuat dan jurnal kas diposting.",
        data=payment,
        meta={"request_id": request.state.request_id},
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
