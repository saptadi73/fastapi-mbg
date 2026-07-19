from datetime import datetime
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.budget.services.budget_service import BudgetService
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.schemas.stock_schema import InventoryBatchCreate, InventoryTransactionCreate
from app.modules.inventory.services.stock_service import StockService
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.procurement.models.goods_receipt import GoodsReceipt
from app.modules.procurement.models.goods_receipt_line import GoodsReceiptLine
from app.modules.procurement.models.purchase_order import PurchaseOrder
from app.modules.procurement.models.purchase_order_line import PurchaseOrderLine
from app.modules.procurement.models.purchase_request import PurchaseRequest
from app.modules.procurement.models.purchase_request_line import PurchaseRequestLine
from app.modules.procurement.models.supplier import Supplier
from app.modules.procurement.models.supplier_invoice import SupplierInvoice
from app.modules.procurement.models.supplier_invoice_line import SupplierInvoiceLine
from app.modules.procurement.models.supplier_payment import SupplierPayment
from app.modules.procurement.models.supplier_price_history import SupplierPriceHistory
from app.modules.procurement.models.supplier_product import SupplierProduct
from app.modules.procurement.repositories.goods_receipt_line_repository import GoodsReceiptLineRepository
from app.modules.procurement.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.procurement.repositories.purchase_order_line_repository import PurchaseOrderLineRepository
from app.modules.procurement.repositories.purchase_order_repository import PurchaseOrderRepository
from app.modules.procurement.repositories.purchase_request_line_repository import PurchaseRequestLineRepository
from app.modules.procurement.repositories.purchase_request_repository import PurchaseRequestRepository
from app.modules.procurement.repositories.supplier_invoice_line_repository import SupplierInvoiceLineRepository
from app.modules.procurement.repositories.supplier_invoice_repository import SupplierInvoiceRepository
from app.modules.procurement.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.modules.procurement.repositories.supplier_price_history_repository import SupplierPriceHistoryRepository
from app.modules.procurement.repositories.supplier_product_repository import SupplierProductRepository
from app.modules.procurement.repositories.supplier_repository import SupplierRepository
from app.modules.procurement.schemas.purchase_request_schema import (
    GoodsReceiptBundleRead,
    GoodsReceiptCreateFromPurchaseOrder,
    GoodsReceiptCreateFromPurchaseRequest,
    PurchaseOrderBundleRead,
    PurchaseOrderCreateFromRequest,
    PurchaseRequestBundleRead,
    SupplierCreate,
    SupplierInvoiceBundleRead,
    SupplierInvoiceCreateFromGoodsReceipt,
    SupplierPaymentCreateFromInvoice,
    SupplierPaymentRead,
    SupplierPriceHistoryCreate,
    SupplierProductCreate,
)
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class ProcurementService:
    PROCUREMENT_BUDGET_ACCOUNT_CODE = "510000"
    PAYABLE_ACCOUNT_CODE = "210000"
    CASH_BANK_ACCOUNT_CODE = "110000"

    def __init__(
        self,
        purchase_request_repository: PurchaseRequestRepository,
        purchase_request_line_repository: PurchaseRequestLineRepository,
        purchase_order_repository: PurchaseOrderRepository,
        purchase_order_line_repository: PurchaseOrderLineRepository,
        goods_receipt_repository: GoodsReceiptRepository,
        goods_receipt_line_repository: GoodsReceiptLineRepository,
        supplier_repository: SupplierRepository,
        supplier_product_repository: SupplierProductRepository,
        supplier_price_history_repository: SupplierPriceHistoryRepository,
        supplier_invoice_repository: SupplierInvoiceRepository,
        supplier_invoice_line_repository: SupplierInvoiceLineRepository,
        supplier_payment_repository: SupplierPaymentRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        meal_plan_service: MealPlanService,
        inventory_balance_repository: InventoryBalanceRepository,
        inventory_batch_repository: InventoryBatchRepository,
        product_repository: ProductRepository,
        stock_service: StockService,
        accounting_service: AccountingService | None = None,
        budget_service: BudgetService | None = None,
    ) -> None:
        self.purchase_request_repository = purchase_request_repository
        self.purchase_request_line_repository = purchase_request_line_repository
        self.purchase_order_repository = purchase_order_repository
        self.purchase_order_line_repository = purchase_order_line_repository
        self.goods_receipt_repository = goods_receipt_repository
        self.goods_receipt_line_repository = goods_receipt_line_repository
        self.supplier_repository = supplier_repository
        self.supplier_product_repository = supplier_product_repository
        self.supplier_price_history_repository = supplier_price_history_repository
        self.supplier_invoice_repository = supplier_invoice_repository
        self.supplier_invoice_line_repository = supplier_invoice_line_repository
        self.supplier_payment_repository = supplier_payment_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.meal_plan_service = meal_plan_service
        self.inventory_balance_repository = inventory_balance_repository
        self.inventory_batch_repository = inventory_batch_repository
        self.product_repository = product_repository
        self.stock_service = stock_service
        self.accounting_service = accounting_service
        self.budget_service = budget_service

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        tenant_id = None
        sppg_id = None
        current_tenant = get_current_tenant()
        current_sppg = get_current_sppg()
        if current_tenant is not None:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(code="INVALID_TENANT_CONTEXT", message="Header X-Tenant-ID tidak valid.") from exc
        if current_sppg is not None:
            try:
                sppg_id = UUID(current_sppg)
            except ValueError as exc:
                raise BadRequestException(code="INVALID_SPPG_CONTEXT", message="Header X-SPPG-ID tidak valid.") from exc
        return tenant_id, sppg_id

    async def list_suppliers(self) -> list[Supplier]:
        tenant_id, _ = self._get_scope()
        return await self.supplier_repository.list_all(tenant_id=tenant_id)

    async def get_supplier(self, supplier_id: UUID) -> Supplier:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise NotFoundException(code="SUPPLIER_NOT_FOUND", message="Supplier tidak ditemukan.")
        tenant_id, _ = self._get_scope()
        if tenant_id is not None and supplier.tenant_id != tenant_id:
            raise NotFoundException(code="SUPPLIER_NOT_FOUND", message="Supplier tidak ditemukan.")
        return supplier

    async def create_supplier(self, payload: SupplierCreate) -> Supplier:
        tenant_id = UUID(payload.tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant supplier tidak ditemukan.")
        existing = await self.supplier_repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(code="SUPPLIER_CODE_ALREADY_EXISTS", message="Kode supplier sudah digunakan pada tenant ini.")
        return await self.supplier_repository.add(
            Supplier(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                supplier_type=payload.supplier_type,
                contact_person=payload.contact_person,
                phone=payload.phone,
                email=payload.email,
                address=payload.address,
                city=payload.city,
                is_active=payload.is_active,
                is_verified=payload.is_verified,
            )
        )

    async def list_supplier_products(self) -> list[SupplierProduct]:
        tenant_id, _ = self._get_scope()
        return await self.supplier_product_repository.list_all(tenant_id=tenant_id)

    async def create_supplier_product(self, payload: SupplierProductCreate) -> SupplierProduct:
        tenant_id = UUID(payload.tenant_id)
        supplier_id = UUID(payload.supplier_id)
        product_id = UUID(payload.product_id)
        purchase_uom_id = UUID(payload.purchase_uom_id)
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None or supplier.tenant_id != tenant_id:
            raise NotFoundException(code="SUPPLIER_NOT_FOUND", message="Supplier produk tidak ditemukan.")
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk supplier tidak ditemukan.")
        if await self.supplier_product_repository.get_by_scope(tenant_id, supplier_id, product_id) is not None:
            raise ConflictException(code="SUPPLIER_PRODUCT_ALREADY_EXISTS", message="Mapping supplier-produk sudah ada.")
        return await self.supplier_product_repository.add(
            SupplierProduct(
                tenant_id=tenant_id,
                supplier_id=supplier_id,
                product_id=product_id,
                purchase_uom_id=purchase_uom_id,
                supplier_product_code=payload.supplier_product_code,
                minimum_order_qty=payload.minimum_order_qty,
                lead_time_days=payload.lead_time_days,
                is_preferred=payload.is_preferred,
                is_active=payload.is_active,
            )
        )

    async def list_supplier_price_histories(self) -> list[SupplierPriceHistory]:
        tenant_id, _ = self._get_scope()
        return await self.supplier_price_history_repository.list_all(tenant_id=tenant_id)

    async def create_supplier_price_history(self, payload: SupplierPriceHistoryCreate) -> SupplierPriceHistory:
        tenant_id = UUID(payload.tenant_id)
        supplier_product_id = UUID(payload.supplier_product_id)
        supplier_product = await self.supplier_product_repository.get_by_id(supplier_product_id)
        if supplier_product is None or supplier_product.tenant_id != tenant_id:
            raise NotFoundException(code="SUPPLIER_PRODUCT_NOT_FOUND", message="Supplier product untuk harga tidak ditemukan.")
        return await self.supplier_price_history_repository.add(
            SupplierPriceHistory(
                tenant_id=tenant_id,
                supplier_product_id=supplier_product_id,
                price=payload.price,
                effective_from=payload.effective_from,
                effective_to=payload.effective_to,
            )
        )

    async def list_purchase_requests(self) -> list[PurchaseRequest]:
        tenant_id, sppg_id = self._get_scope()
        return await self.purchase_request_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_purchase_request(self, purchase_request_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            purchase_request = await self.purchase_request_repository.get_by_id(purchase_request_id)
        else:
            purchase_request = await self.purchase_request_repository.get_by_id_and_scope(purchase_request_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if purchase_request is None:
            raise NotFoundException(code="PURCHASE_REQUEST_NOT_FOUND", message="Purchase request tidak ditemukan.")
        lines = await self.purchase_request_line_repository.list_by_purchase_request(purchase_request_id)
        return {"purchase_request": purchase_request, "lines": lines}

    async def list_purchase_orders(self) -> list[PurchaseOrder]:
        tenant_id, sppg_id = self._get_scope()
        return await self.purchase_order_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_purchase_order(self, purchase_order_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            purchase_order = await self.purchase_order_repository.get_by_id(purchase_order_id)
        else:
            purchase_order = await self.purchase_order_repository.get_by_id_and_scope(purchase_order_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if purchase_order is None:
            raise NotFoundException(code="PURCHASE_ORDER_NOT_FOUND", message="Purchase order tidak ditemukan.")
        lines = await self.purchase_order_line_repository.list_by_purchase_order(purchase_order_id)
        return {"purchase_order": purchase_order, "lines": lines}

    async def create_purchase_order_from_request(self, purchase_request_id: UUID, payload: PurchaseOrderCreateFromRequest) -> dict:
        purchase_request = await self.purchase_request_repository.get_by_id(purchase_request_id)
        if purchase_request is None:
            raise NotFoundException(code="PURCHASE_REQUEST_NOT_FOUND", message="Purchase request tidak ditemukan.")
        supplier = await self.get_supplier(UUID(payload.supplier_id))
        if not supplier.is_active:
            raise BadRequestException(code="SUPPLIER_INACTIVE", message="Supplier tidak aktif.")
        request_lines = await self.purchase_request_line_repository.list_by_purchase_request(purchase_request_id)
        if not request_lines:
            raise BadRequestException(code="PURCHASE_REQUEST_HAS_NO_LINES", message="Purchase request tidak memiliki line.")

        next_number = await self.purchase_order_repository.count_by_tenant(purchase_request.tenant_id) + 1
        order_prefix = "RFQ" if payload.order_type.upper() == "RFQ" else "PO"
        order_number = f"{order_prefix}-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        purchase_order = await self.purchase_order_repository.add(
            PurchaseOrder(
                tenant_id=purchase_request.tenant_id,
                sppg_id=purchase_request.sppg_id,
                supplier_id=supplier.id,
                purchase_request_id=purchase_request.id,
                order_number=order_number,
                order_type=payload.order_type.upper(),
                order_date=payload.order_date,
                expected_date=payload.expected_date,
                status="SENT" if payload.order_type.upper() == "RFQ" else "APPROVED",
                notes=payload.notes,
            )
        )

        created_lines: list[PurchaseOrderLine] = []
        for request_line in request_lines:
            supplier_product = await self.supplier_product_repository.get_by_scope(
                purchase_request.tenant_id,
                supplier.id,
                request_line.product_id,
            )
            latest_price = None
            if supplier_product is not None:
                latest_price = await self.supplier_price_history_repository.get_latest_for_supplier_product(supplier_product.id)
            unit_price = latest_price.price if latest_price is not None else request_line.estimated_unit_cost
            created_lines.append(
                await self.purchase_order_line_repository.add(
                    PurchaseOrderLine(
                        tenant_id=purchase_request.tenant_id,
                        purchase_order_id=purchase_order.id,
                        purchase_request_line_id=request_line.id,
                        product_id=request_line.product_id,
                        uom_id=request_line.uom_id,
                        ordered_quantity=request_line.requested_quantity,
                        unit_price=unit_price,
                        total_amount=round(request_line.requested_quantity * unit_price, 6),
                        line_status="OPEN",
                    )
                )
            )
        purchase_request.status = "ORDERED"
        return PurchaseOrderBundleRead(purchase_order=purchase_order, lines=created_lines).model_dump()

    async def list_goods_receipts(self) -> list[GoodsReceipt]:
        tenant_id, sppg_id = self._get_scope()
        return await self.goods_receipt_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_goods_receipt(self, goods_receipt_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            goods_receipt = await self.goods_receipt_repository.get_by_id(goods_receipt_id)
        else:
            goods_receipt = await self.goods_receipt_repository.get_by_id_and_scope(goods_receipt_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if goods_receipt is None:
            raise NotFoundException(code="GOODS_RECEIPT_NOT_FOUND", message="Goods receipt tidak ditemukan.")
        lines = await self.goods_receipt_line_repository.list_by_goods_receipt(goods_receipt_id)
        return {"goods_receipt": goods_receipt, "lines": lines}

    async def create_purchase_request_from_meal_plan(self, meal_plan_id: UUID) -> dict:
        meal_plan = await self.meal_plan_service.get_meal_plan(meal_plan_id)
        if await self.tenant_repository.get_by_id(meal_plan.tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk purchase request tidak ditemukan.")
        if await self.sppg_repository.get_by_id(meal_plan.sppg_id) is None:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG untuk purchase request tidak ditemukan.")

        requirements = await self.meal_plan_service.calculate_material_requirements(meal_plan_id)
        shortage_lines: list[dict] = []
        for requirement in requirements:
            product_id = UUID(requirement["component_product_id"])
            balances = await self.inventory_balance_repository.list_by_sppg_and_product(meal_plan.sppg_id, product_id)
            available_stock = sum(balance.quantity_available for balance in balances)
            shortage_quantity = round(max(float(requirement["gross_quantity"]) - available_stock, 0), 6)
            if shortage_quantity <= 0:
                continue
            product = await self.product_repository.get_by_id(product_id)
            estimated_unit_cost = product.standard_cost if product else 0
            shortage_lines.append(
                {
                    "product_id": product_id,
                    "uom_id": UUID(requirement["uom_id"]),
                    "requested_quantity": shortage_quantity,
                    "shortage_quantity": shortage_quantity,
                    "estimated_unit_cost": estimated_unit_cost,
                    "estimated_total_cost": round(shortage_quantity * estimated_unit_cost, 6),
                }
            )

        if not shortage_lines:
            raise BadRequestException(code="NO_SHORTAGE_FOR_PURCHASE_REQUEST", message="Tidak ada shortage stock untuk dibuatkan purchase request.")

        next_number = await self.purchase_request_repository.count_by_tenant(meal_plan.tenant_id) + 1
        request_number = f"PR-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        purchase_request = await self.purchase_request_repository.add(
            PurchaseRequest(
                tenant_id=meal_plan.tenant_id,
                sppg_id=meal_plan.sppg_id,
                meal_plan_id=meal_plan.id,
                request_number=request_number,
                status="DRAFT",
                notes=f"Generated from meal plan {meal_plan.id}",
            )
        )

        created_lines: list[PurchaseRequestLine] = []
        for shortage_line in shortage_lines:
            created_lines.append(
                await self.purchase_request_line_repository.add(
                    PurchaseRequestLine(
                        tenant_id=meal_plan.tenant_id,
                        purchase_request_id=purchase_request.id,
                        product_id=shortage_line["product_id"],
                        uom_id=shortage_line["uom_id"],
                        requested_quantity=shortage_line["requested_quantity"],
                        shortage_quantity=shortage_line["shortage_quantity"],
                        estimated_unit_cost=shortage_line["estimated_unit_cost"],
                        estimated_total_cost=shortage_line["estimated_total_cost"],
                    )
                )
            )

        if self.budget_service is not None and self.accounting_service is not None:
            budget_account = await self.accounting_service.get_account_by_code(meal_plan.tenant_id, self.PROCUREMENT_BUDGET_ACCOUNT_CODE)
            if budget_account is not None:
                total_estimated_cost = round(sum(line.estimated_total_cost for line in created_lines), 6)
                await self.budget_service.reserve_budget_by_account(meal_plan.tenant_id, budget_account.id, total_estimated_cost, meal_plan.plan_date)

        return PurchaseRequestBundleRead(purchase_request=purchase_request, lines=created_lines).model_dump()

    async def create_goods_receipt_from_purchase_request(self, purchase_request_id: UUID, payload: GoodsReceiptCreateFromPurchaseRequest, actor: User) -> dict:
        purchase_request = await self.purchase_request_repository.get_by_id(purchase_request_id)
        if purchase_request is None:
            raise NotFoundException(code="PURCHASE_REQUEST_NOT_FOUND", message="Purchase request tidak ditemukan.")

        purchase_request_lines = await self.purchase_request_line_repository.list_by_purchase_request(purchase_request_id)
        if not purchase_request_lines:
            raise BadRequestException(code="PURCHASE_REQUEST_HAS_NO_LINES", message="Purchase request tidak memiliki line untuk diterima.")

        warehouse_id = UUID(payload.warehouse_id)
        warehouses = await self.stock_service.warehouse_repository.list_by_sppg(purchase_request.sppg_id)
        if not any(warehouse.id == warehouse_id for warehouse in warehouses):
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse penerimaan tidak ditemukan.")

        next_number = await self.goods_receipt_repository.count_by_tenant(purchase_request.tenant_id) + 1
        receipt_number = f"GR-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        goods_receipt = await self.goods_receipt_repository.add(
            GoodsReceipt(
                tenant_id=purchase_request.tenant_id,
                sppg_id=purchase_request.sppg_id,
                purchase_request_id=purchase_request.id,
                purchase_order_id=None,
                warehouse_id=warehouse_id,
                receipt_number=receipt_number,
                receipt_date=payload.receipt_date,
                status="POSTED",
                notes=payload.notes,
            )
        )

        created_lines: list[GoodsReceiptLine] = []
        for purchase_request_line in purchase_request_lines:
            goods_receipt_line = await self.goods_receipt_line_repository.add(
                GoodsReceiptLine(
                    tenant_id=purchase_request.tenant_id,
                    goods_receipt_id=goods_receipt.id,
                    purchase_request_line_id=purchase_request_line.id,
                    purchase_order_line_id=None,
                    product_id=purchase_request_line.product_id,
                    uom_id=purchase_request_line.uom_id,
                    received_quantity=purchase_request_line.requested_quantity,
                    unit_cost=purchase_request_line.estimated_unit_cost,
                    total_cost=purchase_request_line.estimated_total_cost,
                )
            )
            created_lines.append(goods_receipt_line)
            await self.stock_service.create_transaction(
                InventoryTransactionCreate(
                    tenant_id=str(purchase_request.tenant_id),
                    sppg_id=str(purchase_request.sppg_id),
                    transaction_type="RECEIPT",
                    reference_type="GOODS_RECEIPT",
                    reference_id=str(goods_receipt.id),
                    product_id=str(purchase_request_line.product_id),
                    destination_warehouse_id=str(warehouse_id),
                    quantity=purchase_request_line.requested_quantity,
                    uom_id=str(purchase_request_line.uom_id),
                    unit_cost=purchase_request_line.estimated_unit_cost,
                    transaction_at=datetime.now(),
                    notes=f"Goods receipt {receipt_number}",
                ),
                actor,
            )

        purchase_request.status = "RECEIVED"
        await self._post_goods_receipt_side_effects(purchase_request.tenant_id, goods_receipt.receipt_date, receipt_number, goods_receipt.id, sum(line.total_cost for line in created_lines), actor)
        return GoodsReceiptBundleRead(goods_receipt=goods_receipt, lines=created_lines).model_dump()

    async def create_goods_receipt_from_purchase_order(self, purchase_order_id: UUID, payload: GoodsReceiptCreateFromPurchaseOrder, actor: User) -> dict:
        purchase_order = await self.purchase_order_repository.get_by_id(purchase_order_id)
        if purchase_order is None:
            raise NotFoundException(code="PURCHASE_ORDER_NOT_FOUND", message="Purchase order tidak ditemukan.")
        purchase_order_lines = await self.purchase_order_line_repository.list_by_purchase_order(purchase_order_id)
        if not purchase_order_lines:
            raise BadRequestException(code="PURCHASE_ORDER_HAS_NO_LINES", message="Purchase order tidak memiliki line untuk diterima.")

        warehouse_id = UUID(payload.warehouse_id)
        next_number = await self.goods_receipt_repository.count_by_tenant(purchase_order.tenant_id) + 1
        receipt_number = f"GR-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        goods_receipt = await self.goods_receipt_repository.add(
            GoodsReceipt(
                tenant_id=purchase_order.tenant_id,
                sppg_id=purchase_order.sppg_id,
                purchase_request_id=purchase_order.purchase_request_id,
                purchase_order_id=purchase_order.id,
                warehouse_id=warehouse_id,
                receipt_number=receipt_number,
                receipt_date=payload.receipt_date,
                status="POSTED",
                notes=payload.notes,
            )
        )

        batch_map: dict[str, dict] = {}
        for item in payload.batch_details:
            if item.get("product_id"):
                batch_map[item["product_id"]] = item

        created_lines: list[GoodsReceiptLine] = []
        for purchase_order_line in purchase_order_lines:
            goods_receipt_line = await self.goods_receipt_line_repository.add(
                GoodsReceiptLine(
                    tenant_id=purchase_order.tenant_id,
                    goods_receipt_id=goods_receipt.id,
                    purchase_request_line_id=purchase_order_line.purchase_request_line_id,
                    purchase_order_line_id=purchase_order_line.id,
                    product_id=purchase_order_line.product_id,
                    uom_id=purchase_order_line.uom_id,
                    received_quantity=purchase_order_line.ordered_quantity,
                    unit_cost=purchase_order_line.unit_price,
                    total_cost=purchase_order_line.total_amount,
                )
            )
            created_lines.append(goods_receipt_line)

            product = await self.product_repository.get_by_id(purchase_order_line.product_id)
            batch_id: str | None = None
            batch_detail = batch_map.get(str(purchase_order_line.product_id))
            if product is not None and (product.track_batch or product.track_expiry):
                if batch_detail is None:
                    raise BadRequestException(
                        code="BATCH_DETAIL_REQUIRED",
                        message="Produk track batch/expiry wajib memiliki detail batch pada goods receipt purchase order.",
                    )
                existing_batch = await self.inventory_batch_repository.get_by_scope(
                    purchase_order.tenant_id,
                    purchase_order_line.product_id,
                    batch_detail["batch_number"],
                )
                if existing_batch is None:
                    batch = await self.stock_service.create_batch(
                        InventoryBatchCreate(
                            tenant_id=str(purchase_order.tenant_id),
                            product_id=str(purchase_order_line.product_id),
                            supplier_id=str(purchase_order.supplier_id),
                            warehouse_id=str(warehouse_id),
                            location_id=payload.location_id,
                            batch_number=batch_detail["batch_number"],
                            production_date=batch_detail.get("production_date"),
                            received_date=payload.receipt_date,
                            expiry_date=batch_detail.get("expiry_date"),
                            quality_status=batch_detail.get("quality_status", "PENDING"),
                            is_blocked=batch_detail.get("is_blocked", False),
                            quantity_on_hand=0,
                        )
                    )
                    batch_id = str(batch.id)
                else:
                    batch_id = str(existing_batch.id)

            await self.stock_service.create_transaction(
                InventoryTransactionCreate(
                    tenant_id=str(purchase_order.tenant_id),
                    sppg_id=str(purchase_order.sppg_id),
                    transaction_type="RECEIPT",
                    reference_type="GOODS_RECEIPT",
                    reference_id=str(goods_receipt.id),
                    product_id=str(purchase_order_line.product_id),
                    batch_id=batch_id,
                    destination_warehouse_id=str(warehouse_id),
                    destination_location_id=payload.location_id,
                    quantity=purchase_order_line.ordered_quantity,
                    uom_id=str(purchase_order_line.uom_id),
                    unit_cost=purchase_order_line.unit_price,
                    transaction_at=datetime.now(),
                    notes=f"Goods receipt {receipt_number} from purchase order {purchase_order.order_number}",
                ),
                actor,
            )

        purchase_order.status = "RECEIVED"
        if purchase_order.purchase_request_id is not None:
            purchase_request = await self.purchase_request_repository.get_by_id(purchase_order.purchase_request_id)
            if purchase_request is not None:
                purchase_request.status = "RECEIVED"
        await self._post_goods_receipt_side_effects(purchase_order.tenant_id, goods_receipt.receipt_date, receipt_number, goods_receipt.id, sum(line.total_cost for line in created_lines), actor)
        return GoodsReceiptBundleRead(goods_receipt=goods_receipt, lines=created_lines).model_dump()

    async def list_supplier_invoices(self) -> list[SupplierInvoice]:
        tenant_id, sppg_id = self._get_scope()
        return await self.supplier_invoice_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_supplier_invoice(self, supplier_invoice_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            supplier_invoice = await self.supplier_invoice_repository.get_by_id(supplier_invoice_id)
        else:
            supplier_invoice = await self.supplier_invoice_repository.get_by_id_and_scope(supplier_invoice_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if supplier_invoice is None:
            raise NotFoundException(code="SUPPLIER_INVOICE_NOT_FOUND", message="Supplier invoice tidak ditemukan.")
        lines = await self.supplier_invoice_line_repository.list_by_supplier_invoice(supplier_invoice_id)
        return {"supplier_invoice": supplier_invoice, "lines": lines}

    async def list_supplier_payments(self) -> list[SupplierPayment]:
        tenant_id, sppg_id = self._get_scope()
        return await self.supplier_payment_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_supplier_payment(self, supplier_payment_id: UUID) -> SupplierPayment:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            supplier_payment = await self.supplier_payment_repository.get_by_id(supplier_payment_id)
        else:
            supplier_payment = await self.supplier_payment_repository.get_by_id_and_scope(supplier_payment_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if supplier_payment is None:
            raise NotFoundException(code="SUPPLIER_PAYMENT_NOT_FOUND", message="Supplier payment tidak ditemukan.")
        return supplier_payment

    async def create_supplier_invoice_from_goods_receipt(self, goods_receipt_id: UUID, payload: SupplierInvoiceCreateFromGoodsReceipt, actor: User) -> dict:
        goods_receipt = await self.goods_receipt_repository.get_by_id(goods_receipt_id)
        if goods_receipt is None:
            raise NotFoundException(code="GOODS_RECEIPT_NOT_FOUND", message="Goods receipt tidak ditemukan.")
        if await self.supplier_invoice_repository.get_by_goods_receipt_id(goods_receipt_id) is not None:
            raise BadRequestException(code="SUPPLIER_INVOICE_ALREADY_EXISTS_FOR_RECEIPT", message="Supplier invoice untuk goods receipt ini sudah ada.")

        goods_receipt_lines = await self.goods_receipt_line_repository.list_by_goods_receipt(goods_receipt_id)
        if not goods_receipt_lines:
            raise BadRequestException(code="GOODS_RECEIPT_HAS_NO_LINES", message="Goods receipt tidak memiliki line untuk dibuatkan invoice.")

        budget_account_id = UUID(payload.budget_account_id) if payload.budget_account_id else None
        total_amount = round(sum(line.total_cost for line in goods_receipt_lines), 6)
        next_number = await self.supplier_invoice_repository.count_by_tenant(goods_receipt.tenant_id) + 1
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        supplier_invoice = await self.supplier_invoice_repository.add(
            SupplierInvoice(
                tenant_id=goods_receipt.tenant_id,
                sppg_id=goods_receipt.sppg_id,
                goods_receipt_id=goods_receipt.id,
                budget_account_id=budget_account_id,
                invoice_number=invoice_number,
                invoice_date=payload.invoice_date,
                due_date=payload.due_date,
                status="POSTED",
                total_amount=total_amount,
                notes=payload.notes,
            )
        )

        created_lines: list[SupplierInvoiceLine] = []
        for goods_receipt_line in goods_receipt_lines:
            created_lines.append(
                await self.supplier_invoice_line_repository.add(
                    SupplierInvoiceLine(
                        tenant_id=goods_receipt.tenant_id,
                        supplier_invoice_id=supplier_invoice.id,
                        goods_receipt_line_id=goods_receipt_line.id,
                        product_id=goods_receipt_line.product_id,
                        uom_id=goods_receipt_line.uom_id,
                        invoiced_quantity=goods_receipt_line.received_quantity,
                        unit_price=goods_receipt_line.unit_cost,
                        total_amount=goods_receipt_line.total_cost,
                        description=f"Invoice line for goods receipt {goods_receipt.receipt_number}",
                    )
                )
            )

        if self.accounting_service is not None and total_amount > 0:
            await self.accounting_service.create_and_post_operational_journal(
                tenant_id=goods_receipt.tenant_id,
                entry_date=supplier_invoice.invoice_date,
                reference=invoice_number,
                description=f"Supplier invoice journal {invoice_number}",
                source_module="procurement",
                source_document_type="supplier_invoice",
                source_document_id=supplier_invoice.id,
                debit_account_code="240000",
                credit_account_code="210000",
                amount=total_amount,
                actor=actor,
            )

        if self.budget_service is not None and budget_account_id is not None and total_amount > 0:
            await self.budget_service.actualize_budget_by_account(goods_receipt.tenant_id, budget_account_id, total_amount, supplier_invoice.invoice_date)

        return SupplierInvoiceBundleRead(supplier_invoice=supplier_invoice, lines=created_lines).model_dump()

    async def create_supplier_payment_from_invoice(self, supplier_invoice_id: UUID, payload: SupplierPaymentCreateFromInvoice, actor: User) -> dict:
        supplier_invoice = await self.supplier_invoice_repository.get_by_id(supplier_invoice_id)
        if supplier_invoice is None:
            raise NotFoundException(code="SUPPLIER_INVOICE_NOT_FOUND", message="Supplier invoice tidak ditemukan.")
        if await self.supplier_payment_repository.get_by_supplier_invoice_id(supplier_invoice_id) is not None:
            raise BadRequestException(code="SUPPLIER_PAYMENT_ALREADY_EXISTS_FOR_INVOICE", message="Supplier payment untuk supplier invoice ini sudah ada.")
        if supplier_invoice.status != "POSTED":
            raise BadRequestException(code="SUPPLIER_PAYMENT_INVALID_INVOICE_STATUS", message="Hanya supplier invoice berstatus POSTED yang bisa dibayar.")

        bank_account_id = UUID(payload.bank_account_id) if payload.bank_account_id else None
        next_number = await self.supplier_payment_repository.count_by_tenant(supplier_invoice.tenant_id) + 1
        payment_number = f"PAY-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
        supplier_payment = await self.supplier_payment_repository.add(
            SupplierPayment(
                tenant_id=supplier_invoice.tenant_id,
                sppg_id=supplier_invoice.sppg_id,
                supplier_invoice_id=supplier_invoice.id,
                bank_account_id=bank_account_id,
                payment_number=payment_number,
                payment_date=payload.payment_date,
                status="POSTED",
                total_amount=supplier_invoice.total_amount,
                notes=payload.notes,
            )
        )

        if self.accounting_service is not None and supplier_payment.total_amount > 0:
            await self.accounting_service.create_and_post_operational_journal(
                tenant_id=supplier_invoice.tenant_id,
                entry_date=supplier_payment.payment_date,
                reference=payment_number,
                description=f"Supplier payment journal {payment_number}",
                source_module="procurement",
                source_document_type="supplier_payment",
                source_document_id=supplier_payment.id,
                debit_account_code=self.PAYABLE_ACCOUNT_CODE,
                credit_account_code=self.CASH_BANK_ACCOUNT_CODE,
                amount=supplier_payment.total_amount,
                actor=actor,
            )

        supplier_invoice.status = "PAID"
        return SupplierPaymentRead.model_validate(supplier_payment).model_dump()

    async def _post_goods_receipt_side_effects(
        self,
        tenant_id: UUID,
        receipt_date,
        receipt_number: str,
        goods_receipt_id: UUID,
        total_receipt_cost: float,
        actor: User,
    ) -> None:
        total_receipt_cost = round(total_receipt_cost, 6)
        if self.budget_service is not None and self.accounting_service is not None and total_receipt_cost > 0:
            budget_account = await self.accounting_service.get_account_by_code(tenant_id, self.PROCUREMENT_BUDGET_ACCOUNT_CODE)
            if budget_account is not None:
                await self.budget_service.commit_budget_by_account(tenant_id, budget_account.id, total_receipt_cost, receipt_date)
        if self.accounting_service is not None and total_receipt_cost > 0:
            await self.accounting_service.create_and_post_operational_journal(
                tenant_id=tenant_id,
                entry_date=receipt_date,
                reference=receipt_number,
                description=f"Inventory journal goods receipt {receipt_number}",
                source_module="procurement",
                source_document_type="goods_receipt",
                source_document_id=goods_receipt_id,
                debit_account_code="130000",
                credit_account_code="240000",
                amount=total_receipt_cost,
                actor=actor,
            )
