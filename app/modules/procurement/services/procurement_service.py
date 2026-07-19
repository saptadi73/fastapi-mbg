from datetime import datetime
from uuid import UUID

from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.budget.services.budget_service import BudgetService
from app.modules.identity.models.user import User
from app.modules.inventory.schemas.stock_schema import InventoryTransactionCreate
from app.modules.inventory.services.stock_service import StockService
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.procurement.models.goods_receipt import GoodsReceipt
from app.modules.procurement.models.goods_receipt_line import GoodsReceiptLine
from app.modules.procurement.models.purchase_request import PurchaseRequest
from app.modules.procurement.models.purchase_request_line import PurchaseRequestLine
from app.modules.procurement.models.supplier_invoice import SupplierInvoice
from app.modules.procurement.models.supplier_invoice_line import SupplierInvoiceLine
from app.modules.procurement.models.supplier_payment import SupplierPayment
from app.modules.procurement.repositories.goods_receipt_line_repository import GoodsReceiptLineRepository
from app.modules.procurement.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.procurement.repositories.purchase_request_line_repository import PurchaseRequestLineRepository
from app.modules.procurement.repositories.purchase_request_repository import PurchaseRequestRepository
from app.modules.procurement.repositories.supplier_invoice_line_repository import SupplierInvoiceLineRepository
from app.modules.procurement.repositories.supplier_invoice_repository import SupplierInvoiceRepository
from app.modules.procurement.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.modules.procurement.schemas.purchase_request_schema import (
    GoodsReceiptBundleRead,
    GoodsReceiptCreateFromPurchaseRequest,
    PurchaseRequestBundleRead,
    SupplierInvoiceBundleRead,
    SupplierInvoiceCreateFromGoodsReceipt,
    SupplierPaymentCreateFromInvoice,
    SupplierPaymentRead,
)
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class ProcurementService:
    PROCUREMENT_BUDGET_ACCOUNT_CODE = "510000"
    PAYABLE_ACCOUNT_CODE = "210000"
    CASH_BANK_ACCOUNT_CODE = "110000"

    def __init__(
        self,
        purchase_request_repository: PurchaseRequestRepository,
        purchase_request_line_repository: PurchaseRequestLineRepository,
        goods_receipt_repository: GoodsReceiptRepository,
        goods_receipt_line_repository: GoodsReceiptLineRepository,
        supplier_invoice_repository: SupplierInvoiceRepository,
        supplier_invoice_line_repository: SupplierInvoiceLineRepository,
        supplier_payment_repository: SupplierPaymentRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        meal_plan_service: MealPlanService,
        inventory_balance_repository: InventoryBalanceRepository,
        product_repository: ProductRepository,
        stock_service: StockService,
        accounting_service: AccountingService | None = None,
        budget_service: BudgetService | None = None,
    ) -> None:
        self.purchase_request_repository = purchase_request_repository
        self.purchase_request_line_repository = purchase_request_line_repository
        self.goods_receipt_repository = goods_receipt_repository
        self.goods_receipt_line_repository = goods_receipt_line_repository
        self.supplier_invoice_repository = supplier_invoice_repository
        self.supplier_invoice_line_repository = supplier_invoice_line_repository
        self.supplier_payment_repository = supplier_payment_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.meal_plan_service = meal_plan_service
        self.inventory_balance_repository = inventory_balance_repository
        self.product_repository = product_repository
        self.stock_service = stock_service
        self.accounting_service = accounting_service
        self.budget_service = budget_service

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

    async def list_supplier_invoices(self) -> list[SupplierInvoice]:
        return await self.supplier_invoice_repository.list_all()

    async def get_supplier_invoice(self, supplier_invoice_id: UUID) -> dict:
        supplier_invoice = await self.supplier_invoice_repository.get_by_id(supplier_invoice_id)
        if supplier_invoice is None:
            raise NotFoundException(code="SUPPLIER_INVOICE_NOT_FOUND", message="Supplier invoice tidak ditemukan.")
        lines = await self.supplier_invoice_line_repository.list_by_supplier_invoice(supplier_invoice_id)
        return {"supplier_invoice": supplier_invoice, "lines": lines}

    async def list_supplier_payments(self) -> list[SupplierPayment]:
        return await self.supplier_payment_repository.list_all()

    async def get_supplier_payment(self, supplier_payment_id: UUID) -> SupplierPayment:
        supplier_payment = await self.supplier_payment_repository.get_by_id(supplier_payment_id)
        if supplier_payment is None:
            raise NotFoundException(code="SUPPLIER_PAYMENT_NOT_FOUND", message="Supplier payment tidak ditemukan.")
        return supplier_payment

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

        if self.budget_service is not None and self.accounting_service is not None:
            budget_account = await self.accounting_service.get_account_by_code(
                meal_plan.tenant_id,
                self.PROCUREMENT_BUDGET_ACCOUNT_CODE,
            )
            if budget_account is not None:
                total_estimated_cost = round(sum(line.estimated_total_cost for line in created_lines), 6)
                await self.budget_service.reserve_budget_by_account(
                    meal_plan.tenant_id,
                    budget_account.id,
                    total_estimated_cost,
                    meal_plan.plan_date,
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
        total_receipt_cost = round(sum(line.total_cost for line in created_lines), 6)
        if self.budget_service is not None and self.accounting_service is not None and total_receipt_cost > 0:
            budget_account = await self.accounting_service.get_account_by_code(
                purchase_request.tenant_id,
                self.PROCUREMENT_BUDGET_ACCOUNT_CODE,
            )
            if budget_account is not None:
                await self.budget_service.commit_budget_by_account(
                    purchase_request.tenant_id,
                    budget_account.id,
                    total_receipt_cost,
                    goods_receipt.receipt_date,
                )
        if self.accounting_service is not None:
            if total_receipt_cost > 0:
                await self.accounting_service.create_and_post_operational_journal(
                    tenant_id=purchase_request.tenant_id,
                    entry_date=goods_receipt.receipt_date,
                    reference=receipt_number,
                    description=f"Inventory journal goods receipt {receipt_number}",
                    source_module="procurement",
                    source_document_type="goods_receipt",
                    source_document_id=goods_receipt.id,
                    debit_account_code="130000",
                    credit_account_code="240000",
                    amount=total_receipt_cost,
                    actor=actor,
                )
        return GoodsReceiptBundleRead(goods_receipt=goods_receipt, lines=created_lines).model_dump()

    async def create_supplier_invoice_from_goods_receipt(
        self,
        goods_receipt_id: UUID,
        payload: SupplierInvoiceCreateFromGoodsReceipt,
        actor: User,
    ) -> dict:
        goods_receipt = await self.goods_receipt_repository.get_by_id(goods_receipt_id)
        if goods_receipt is None:
            raise NotFoundException(code="GOODS_RECEIPT_NOT_FOUND", message="Goods receipt tidak ditemukan.")
        if await self.supplier_invoice_repository.get_by_goods_receipt_id(goods_receipt_id) is not None:
            raise BadRequestException(
                code="SUPPLIER_INVOICE_ALREADY_EXISTS_FOR_RECEIPT",
                message="Supplier invoice untuk goods receipt ini sudah ada.",
            )

        goods_receipt_lines = await self.goods_receipt_line_repository.list_by_goods_receipt(goods_receipt_id)
        if not goods_receipt_lines:
            raise BadRequestException(
                code="GOODS_RECEIPT_HAS_NO_LINES",
                message="Goods receipt tidak memiliki line untuk dibuatkan invoice.",
            )

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
            await self.budget_service.actualize_budget_by_account(
                goods_receipt.tenant_id,
                budget_account_id,
                total_amount,
                supplier_invoice.invoice_date,
            )

        return SupplierInvoiceBundleRead(supplier_invoice=supplier_invoice, lines=created_lines).model_dump()

    async def create_supplier_payment_from_invoice(
        self,
        supplier_invoice_id: UUID,
        payload: SupplierPaymentCreateFromInvoice,
        actor: User,
    ) -> dict:
        supplier_invoice = await self.supplier_invoice_repository.get_by_id(supplier_invoice_id)
        if supplier_invoice is None:
            raise NotFoundException(code="SUPPLIER_INVOICE_NOT_FOUND", message="Supplier invoice tidak ditemukan.")
        if await self.supplier_payment_repository.get_by_supplier_invoice_id(supplier_invoice_id) is not None:
            raise BadRequestException(
                code="SUPPLIER_PAYMENT_ALREADY_EXISTS_FOR_INVOICE",
                message="Supplier payment untuk supplier invoice ini sudah ada.",
            )
        if supplier_invoice.status != "POSTED":
            raise BadRequestException(
                code="SUPPLIER_PAYMENT_INVALID_INVOICE_STATUS",
                message="Hanya supplier invoice berstatus POSTED yang bisa dibayar.",
            )

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
