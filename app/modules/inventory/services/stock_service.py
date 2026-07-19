from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.identity.models.user import User
from app.modules.inventory.models.inventory_balance import InventoryBalance
from app.modules.inventory.models.inventory_transaction import InventoryTransaction
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_schema import InventoryTransactionCreate
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.exceptions.base import BadRequestException, NotFoundException

INBOUND_TRANSACTION_TYPES = {"RECEIPT", "ADJUSTMENT_IN", "DONATION_RECEIPT", "PRODUCTION_RETURN"}
OUTBOUND_TRANSACTION_TYPES = {
    "ISSUE_TO_PRODUCTION",
    "DELIVERY_ISSUE",
    "ADJUSTMENT_OUT",
    "DONATION_DISTRIBUTION",
    "WASTE",
    "EXPIRED",
}
TRANSFER_TRANSACTION_TYPES = {"INTERNAL_TRANSFER"}
SUPPORTED_TRANSACTION_TYPES = INBOUND_TRANSACTION_TYPES | OUTBOUND_TRANSACTION_TYPES | TRANSFER_TRANSACTION_TYPES


class StockService:
    def __init__(
        self,
        transaction_repository: InventoryTransactionRepository,
        balance_repository: InventoryBalanceRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        product_repository: ProductRepository,
        uom_repository: UomRepository,
        warehouse_repository: WarehouseRepository,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.balance_repository = balance_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.product_repository = product_repository
        self.uom_repository = uom_repository
        self.warehouse_repository = warehouse_repository

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        tenant_id = None
        sppg_id = None
        current_tenant = get_current_tenant()
        current_sppg = get_current_sppg()
        if current_tenant is not None:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_TENANT_CONTEXT",
                    message="Header X-Tenant-ID tidak valid.",
                ) from exc
        if current_sppg is not None:
            try:
                sppg_id = UUID(current_sppg)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_SPPG_CONTEXT",
                    message="Header X-SPPG-ID tidak valid.",
                ) from exc
        return tenant_id, sppg_id

    async def list_transactions(self) -> list[InventoryTransaction]:
        tenant_id, sppg_id = self._get_scope()
        return await self.transaction_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_balances(self) -> list[InventoryBalance]:
        tenant_id, sppg_id = self._get_scope()
        return await self.balance_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_transaction(self, payload: InventoryTransactionCreate, actor: User) -> InventoryTransaction:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        product_id = UUID(payload.product_id)
        uom_id = UUID(payload.uom_id)
        reference_id = UUID(payload.reference_id) if payload.reference_id else None
        source_warehouse_id = UUID(payload.source_warehouse_id) if payload.source_warehouse_id else None
        destination_warehouse_id = UUID(payload.destination_warehouse_id) if payload.destination_warehouse_id else None

        if payload.transaction_type not in SUPPORTED_TRANSACTION_TYPES:
            raise BadRequestException(
                code="UNSUPPORTED_INVENTORY_TRANSACTION_TYPE",
                message="Tipe transaksi inventory belum didukung.",
            )
        if payload.quantity <= 0:
            raise BadRequestException(code="INVALID_QUANTITY", message="Quantity harus lebih besar dari nol.")

        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk inventory tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG untuk inventory tidak ditemukan.")
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk inventory tidak ditemukan.")
        uom = await self.uom_repository.get_by_id(uom_id)
        if uom is None or uom.tenant_id != tenant_id:
            raise NotFoundException(code="UOM_NOT_FOUND", message="UoM inventory tidak ditemukan.")

        source_warehouse = None
        if source_warehouse_id:
            source_warehouse = await self.warehouse_repository.get_by_id(source_warehouse_id)
            if source_warehouse is None or source_warehouse.tenant_id != tenant_id:
                raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse sumber tidak ditemukan.")

        destination_warehouse = None
        if destination_warehouse_id:
            destination_warehouse = await self.warehouse_repository.get_by_id(destination_warehouse_id)
            if destination_warehouse is None or destination_warehouse.tenant_id != tenant_id:
                raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse tujuan tidak ditemukan.")

        if payload.transaction_type in INBOUND_TRANSACTION_TYPES and destination_warehouse is None:
            raise BadRequestException(
                code="DESTINATION_WAREHOUSE_REQUIRED",
                message="Warehouse tujuan wajib untuk transaksi masuk.",
            )
        if payload.transaction_type in OUTBOUND_TRANSACTION_TYPES and source_warehouse is None:
            raise BadRequestException(
                code="SOURCE_WAREHOUSE_REQUIRED",
                message="Warehouse sumber wajib untuk transaksi keluar.",
            )
        if payload.transaction_type in TRANSFER_TRANSACTION_TYPES:
            if source_warehouse is None or destination_warehouse is None:
                raise BadRequestException(
                    code="WAREHOUSE_TRANSFER_INCOMPLETE",
                    message="Warehouse sumber dan tujuan wajib untuk transfer internal.",
                )
            if source_warehouse.id == destination_warehouse.id:
                raise BadRequestException(
                    code="WAREHOUSE_TRANSFER_SAME_LOCATION",
                    message="Warehouse sumber dan tujuan tidak boleh sama.",
                )

        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            transaction_type=payload.transaction_type,
            reference_type=payload.reference_type,
            reference_id=reference_id,
            product_id=product_id,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            quantity=payload.quantity,
            uom_id=uom_id,
            unit_cost=payload.unit_cost,
            total_cost=payload.quantity * payload.unit_cost,
            transaction_at=payload.transaction_at,
            posted_by=actor.id,
            notes=payload.notes,
        )
        transaction = await self.transaction_repository.add(transaction)

        if payload.transaction_type in INBOUND_TRANSACTION_TYPES:
            await self._increase_balance(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                warehouse_id=destination_warehouse_id,
                product_id=product_id,
                quantity=payload.quantity,
                unit_cost=payload.unit_cost,
            )
        elif payload.transaction_type in OUTBOUND_TRANSACTION_TYPES:
            await self._decrease_balance(
                warehouse_id=source_warehouse_id,
                product_id=product_id,
                quantity=payload.quantity,
            )
        else:
            await self._decrease_balance(
                warehouse_id=source_warehouse_id,
                product_id=product_id,
                quantity=payload.quantity,
            )
            await self._increase_balance(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                warehouse_id=destination_warehouse_id,
                product_id=product_id,
                quantity=payload.quantity,
                unit_cost=payload.unit_cost,
            )

        return transaction

    async def record_reserved_issue_transaction(self, payload: InventoryTransactionCreate, actor: User) -> InventoryTransaction:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        product_id = UUID(payload.product_id)
        uom_id = UUID(payload.uom_id)
        reference_id = UUID(payload.reference_id) if payload.reference_id else None
        source_warehouse_id = UUID(payload.source_warehouse_id) if payload.source_warehouse_id else None

        if payload.transaction_type != "ISSUE_TO_PRODUCTION":
            raise BadRequestException(
                code="INVALID_RESERVED_ISSUE_TRANSACTION_TYPE",
                message="Reserved issue hanya mendukung ISSUE_TO_PRODUCTION.",
            )
        if payload.quantity <= 0:
            raise BadRequestException(code="INVALID_QUANTITY", message="Quantity harus lebih besar dari nol.")

        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk inventory tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG untuk inventory tidak ditemukan.")
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk inventory tidak ditemukan.")
        uom = await self.uom_repository.get_by_id(uom_id)
        if uom is None or uom.tenant_id != tenant_id:
            raise NotFoundException(code="UOM_NOT_FOUND", message="UoM inventory tidak ditemukan.")
        if source_warehouse_id is None:
            raise BadRequestException(
                code="SOURCE_WAREHOUSE_REQUIRED",
                message="Warehouse sumber wajib untuk transaksi keluar.",
            )
        source_warehouse = await self.warehouse_repository.get_by_id(source_warehouse_id)
        if source_warehouse is None or source_warehouse.tenant_id != tenant_id:
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse sumber tidak ditemukan.")

        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            transaction_type=payload.transaction_type,
            reference_type=payload.reference_type,
            reference_id=reference_id,
            product_id=product_id,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=None,
            quantity=payload.quantity,
            uom_id=uom_id,
            unit_cost=payload.unit_cost,
            total_cost=payload.quantity * payload.unit_cost,
            transaction_at=payload.transaction_at,
            posted_by=actor.id,
            notes=payload.notes,
        )
        return await self.transaction_repository.add(transaction)

    async def _increase_balance(
        self,
        *,
        tenant_id: UUID,
        sppg_id: UUID,
        warehouse_id: UUID | None,
        product_id: UUID,
        quantity: float,
        unit_cost: float,
    ) -> InventoryBalance:
        if warehouse_id is None:
            raise BadRequestException(code="DESTINATION_WAREHOUSE_REQUIRED", message="Warehouse tujuan wajib diisi.")
        balance = await self.balance_repository.get_by_warehouse_and_product(warehouse_id, product_id)
        if balance is None:
            balance = InventoryBalance(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity_on_hand=0,
                quantity_reserved=0,
                quantity_available=0,
                average_cost=0,
            )
            balance = await self.balance_repository.add(balance)

        current_total_cost = balance.quantity_on_hand * balance.average_cost
        incoming_total_cost = quantity * unit_cost
        new_quantity_on_hand = balance.quantity_on_hand + quantity
        balance.quantity_on_hand = new_quantity_on_hand
        balance.quantity_available = new_quantity_on_hand - balance.quantity_reserved
        balance.average_cost = (
            (current_total_cost + incoming_total_cost) / new_quantity_on_hand if new_quantity_on_hand > 0 else 0
        )
        return balance

    async def _decrease_balance(self, *, warehouse_id: UUID | None, product_id: UUID, quantity: float) -> InventoryBalance:
        if warehouse_id is None:
            raise BadRequestException(code="SOURCE_WAREHOUSE_REQUIRED", message="Warehouse sumber wajib diisi.")
        balance = await self.balance_repository.get_by_warehouse_and_product(warehouse_id, product_id)
        if balance is None or balance.quantity_available < quantity:
            raise BadRequestException(
                code="INSUFFICIENT_STOCK",
                message="Stok tersedia tidak cukup untuk memproses transaksi.",
            )
        balance.quantity_on_hand -= quantity
        balance.quantity_available = balance.quantity_on_hand - balance.quantity_reserved
        return balance
