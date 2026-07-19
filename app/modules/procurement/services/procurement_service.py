from datetime import datetime
from uuid import UUID

from app.modules.identity.models.user import User
from app.modules.inventory.schemas.stock_schema import InventoryTransactionCreate
from app.modules.inventory.services.stock_service import StockService
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.procurement.models.goods_receipt import GoodsReceipt
from app.modules.procurement.models.goods_receipt_line import GoodsReceiptLine
from app.modules.procurement.models.purchase_request import PurchaseRequest
from app.modules.procurement.models.purchase_request_line import PurchaseRequestLine
from app.modules.procurement.repositories.goods_receipt_line_repository import GoodsReceiptLineRepository
from app.modules.procurement.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.procurement.repositories.purchase_request_line_repository import PurchaseRequestLineRepository
from app.modules.procurement.repositories.purchase_request_repository import PurchaseRequestRepository
from app.modules.procurement.schemas.purchase_request_schema import (
    GoodsReceiptBundleRead,
    GoodsReceiptCreateFromPurchaseRequest,
    PurchaseRequestBundleRead,
)
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class ProcurementService:
    def __init__(
        self,
        purchase_request_repository: PurchaseRequestRepository,
        purchase_request_line_repository: PurchaseRequestLineRepository,
        goods_receipt_repository: GoodsReceiptRepository,
        goods_receipt_line_repository: GoodsReceiptLineRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        meal_plan_service: MealPlanService,
        inventory_balance_repository: InventoryBalanceRepository,
        product_repository: ProductRepository,
        stock_service: StockService,
    ) -> None:
        self.purchase_request_repository = purchase_request_repository
        self.purchase_request_line_repository = purchase_request_line_repository
        self.goods_receipt_repository = goods_receipt_repository
        self.goods_receipt_line_repository = goods_receipt_line_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.meal_plan_service = meal_plan_service
        self.inventory_balance_repository = inventory_balance_repository
        self.product_repository = product_repository
        self.stock_service = stock_service

    async def list_purchase_requests(self) -> list[PurchaseRequest]:
        return await self.purchase_request_repository.list_all()

    async def get_purchase_request(self, purchase_request_id: UUID) -> dict:
        purchase_request = await self.purchase_request_repository.get_by_id(purchase_request_id)
        if purchase_request is None:
            raise NotFoundException(code="PURCHASE_REQUEST_NOT_FOUND", message="Purchase request tidak ditemukan.")
        lines = await self.purchase_request_line_repository.list_by_purchase_request(purchase_request_id)
        return {
            "purchase_request": purchase_request,
            "lines": lines,
        }

    async def list_goods_receipts(self) -> list[GoodsReceipt]:
        return await self.goods_receipt_repository.list_all()

    async def get_goods_receipt(self, goods_receipt_id: UUID) -> dict:
        goods_receipt = await self.goods_receipt_repository.get_by_id(goods_receipt_id)
        if goods_receipt is None:
            raise NotFoundException(code="GOODS_RECEIPT_NOT_FOUND", message="Goods receipt tidak ditemukan.")
        lines = await self.goods_receipt_line_repository.list_by_goods_receipt(goods_receipt_id)
        return {
            "goods_receipt": goods_receipt,
            "lines": lines,
        }

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
            raise BadRequestException(
                code="NO_SHORTAGE_FOR_PURCHASE_REQUEST",
                message="Tidak ada shortage stock untuk dibuatkan purchase request.",
            )

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

        return PurchaseRequestBundleRead(
            purchase_request=purchase_request,
            lines=created_lines,
        ).model_dump()

    async def create_goods_receipt_from_purchase_request(
        self,
        purchase_request_id: UUID,
        payload: GoodsReceiptCreateFromPurchaseRequest,
        actor: User,
    ) -> dict:
        purchase_request = await self.purchase_request_repository.get_by_id(purchase_request_id)
        if purchase_request is None:
            raise NotFoundException(code="PURCHASE_REQUEST_NOT_FOUND", message="Purchase request tidak ditemukan.")

        purchase_request_lines = await self.purchase_request_line_repository.list_by_purchase_request(purchase_request_id)
        if not purchase_request_lines:
            raise BadRequestException(
                code="PURCHASE_REQUEST_HAS_NO_LINES",
                message="Purchase request tidak memiliki line untuk diterima.",
            )

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
        return GoodsReceiptBundleRead(goods_receipt=goods_receipt, lines=created_lines).model_dump()
