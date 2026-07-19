from datetime import date
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.identity.models.user import User
from app.modules.inventory.models.inventory_balance import InventoryBalance
from app.modules.inventory.models.inventory_batch import InventoryBatch
from app.modules.inventory.models.inventory_transaction import InventoryTransaction
from app.modules.inventory.models.stock_location import StockLocation
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.stock_location_repository import StockLocationRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_schema import (
    FEFOIssuePreviewRead,
    FEFOIssuePreviewRequest,
    InventoryBatchCreate,
    InventoryTransactionCreate,
    StockLocationCreate,
)
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException

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
        location_repository: StockLocationRepository,
        batch_repository: InventoryBatchRepository,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.balance_repository = balance_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.product_repository = product_repository
        self.uom_repository = uom_repository
        self.warehouse_repository = warehouse_repository
        self.location_repository = location_repository
        self.batch_repository = batch_repository

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

    async def list_transactions(self) -> list[InventoryTransaction]:
        tenant_id, sppg_id = self._get_scope()
        return await self.transaction_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_balances(self) -> list[InventoryBalance]:
        tenant_id, sppg_id = self._get_scope()
        return await self.balance_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_locations(self) -> list[StockLocation]:
        tenant_id, sppg_id = self._get_scope()
        return await self.location_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_batches(self) -> list[InventoryBatch]:
        tenant_id, _ = self._get_scope()
        return await self.batch_repository.list_all(tenant_id=tenant_id)

    async def list_expiry_alerts(self, days_ahead: int = 14) -> list[InventoryBatch]:
        tenant_id, _ = self._get_scope()
        if tenant_id is None:
            raise BadRequestException(code="TENANT_CONTEXT_REQUIRED", message="Header X-Tenant-ID wajib dikirim untuk expiry alert.")
        cutoff = date.fromordinal(date(2026, 7, 19).toordinal() + max(days_ahead, 0))
        return await self.batch_repository.list_expiring(tenant_id, cutoff)

    async def create_location(self, payload: StockLocationCreate) -> StockLocation:
        tenant_id = UUID(payload.tenant_id)
        warehouse_id = UUID(payload.warehouse_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        parent_id = UUID(payload.parent_id) if payload.parent_id else None
        enforce_tenant_write_scope(tenant_id)
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if warehouse is None or warehouse.tenant_id != tenant_id:
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse untuk stock location tidak ditemukan.")
        if sppg_id is not None and warehouse.sppg_id != sppg_id:
            raise BadRequestException(code="LOCATION_SPPG_MISMATCH", message="SPPG stock location tidak sesuai dengan warehouse.")
        if parent_id is not None:
            parent = await self.location_repository.get_by_id(parent_id)
            if parent is None or parent.tenant_id != tenant_id or parent.warehouse_id != warehouse_id:
                raise NotFoundException(code="PARENT_LOCATION_NOT_FOUND", message="Parent stock location tidak ditemukan.")
        existing = await self.location_repository.get_by_tenant_warehouse_code(tenant_id, warehouse_id, payload.code)
        if existing is not None:
            raise ConflictException(code="STOCK_LOCATION_CODE_ALREADY_EXISTS", message="Kode stock location sudah digunakan pada warehouse ini.")
        location = StockLocation(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            sppg_id=sppg_id or warehouse.sppg_id,
            parent_id=parent_id,
            code=payload.code,
            name=payload.name,
            location_type=payload.location_type,
            is_active=payload.is_active,
        )
        return await self.location_repository.add(location)

    async def create_batch(self, payload: InventoryBatchCreate) -> InventoryBatch:
        tenant_id = UUID(payload.tenant_id)
        product_id = UUID(payload.product_id)
        warehouse_id = UUID(payload.warehouse_id) if payload.warehouse_id else None
        location_id = UUID(payload.location_id) if payload.location_id else None
        supplier_id = UUID(payload.supplier_id) if payload.supplier_id else None
        enforce_tenant_write_scope(tenant_id)
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.tenant_id != tenant_id:
            raise NotFoundException(code="PRODUCT_NOT_FOUND", message="Produk batch inventory tidak ditemukan.")
        existing = await self.batch_repository.get_by_scope(tenant_id, product_id, payload.batch_number)
        if existing is not None:
            raise ConflictException(code="INVENTORY_BATCH_ALREADY_EXISTS", message="Batch inventory untuk produk ini sudah ada.")
        if location_id is not None:
            location = await self.location_repository.get_by_id(location_id)
            if location is None or location.tenant_id != tenant_id:
                raise NotFoundException(code="STOCK_LOCATION_NOT_FOUND", message="Stock location batch tidak ditemukan.")
            warehouse_id = location.warehouse_id
        elif warehouse_id is not None:
            warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
            if warehouse is None or warehouse.tenant_id != tenant_id:
                raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse batch tidak ditemukan.")
        batch = InventoryBatch(
            tenant_id=tenant_id,
            product_id=product_id,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            batch_number=payload.batch_number,
            production_date=payload.production_date,
            received_date=payload.received_date,
            expiry_date=payload.expiry_date,
            quality_status=payload.quality_status,
            is_blocked=payload.is_blocked,
            quantity_on_hand=payload.quantity_on_hand,
            quantity_reserved=0,
            quantity_available=payload.quantity_on_hand,
        )
        return await self.batch_repository.add(batch)

    async def suggest_fefo_issue(self, payload: FEFOIssuePreviewRequest) -> dict:
        tenant_id = UUID(payload.tenant_id)
        product_id = UUID(payload.product_id)
        warehouse_id = UUID(payload.warehouse_id) if payload.warehouse_id else None
        if payload.required_quantity <= 0:
            raise BadRequestException(code="INVALID_REQUIRED_QUANTITY", message="Required quantity FEFO harus lebih besar dari nol.")
        candidates = await self.batch_repository.list_fefo_candidates(tenant_id, product_id, warehouse_id)
        remaining = payload.required_quantity
        issues: list[dict] = []
        for batch in candidates:
            if remaining <= 0:
                break
            issue_qty = min(batch.quantity_available, remaining)
            issues.append(
                {
                    "batch_id": batch.id,
                    "batch_number": batch.batch_number,
                    "expiry_date": batch.expiry_date,
                    "available_quantity": batch.quantity_available,
                    "issue_quantity": round(issue_qty, 6),
                }
            )
            remaining = round(remaining - issue_qty, 6)
        fulfilled = round(payload.required_quantity - remaining, 6)
        return FEFOIssuePreviewRead(
            product_id=product_id,
            warehouse_id=warehouse_id,
            required_quantity=payload.required_quantity,
            fulfilled_quantity=fulfilled,
            shortage_quantity=max(remaining, 0),
            candidates=issues,
        ).model_dump()

    async def create_transaction(self, payload: InventoryTransactionCreate, actor: User) -> InventoryTransaction:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        product_id = UUID(payload.product_id)
        uom_id = UUID(payload.uom_id)
        reference_id = UUID(payload.reference_id) if payload.reference_id else None
        batch_id = UUID(payload.batch_id) if payload.batch_id else None
        source_warehouse_id = UUID(payload.source_warehouse_id) if payload.source_warehouse_id else None
        destination_warehouse_id = UUID(payload.destination_warehouse_id) if payload.destination_warehouse_id else None
        source_location_id = UUID(payload.source_location_id) if payload.source_location_id else None
        destination_location_id = UUID(payload.destination_location_id) if payload.destination_location_id else None

        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)

        if payload.transaction_type not in SUPPORTED_TRANSACTION_TYPES:
            raise BadRequestException(code="UNSUPPORTED_INVENTORY_TRANSACTION_TYPE", message="Tipe transaksi inventory belum didukung.")
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

        source_warehouse = await self._validate_warehouse(source_warehouse_id, tenant_id, "Warehouse sumber tidak ditemukan.")
        destination_warehouse = await self._validate_warehouse(destination_warehouse_id, tenant_id, "Warehouse tujuan tidak ditemukan.")
        source_location = await self._validate_location(source_location_id, source_warehouse_id, tenant_id, "Stock location sumber tidak ditemukan.")
        destination_location = await self._validate_location(destination_location_id, destination_warehouse_id, tenant_id, "Stock location tujuan tidak ditemukan.")

        if payload.transaction_type in INBOUND_TRANSACTION_TYPES and destination_warehouse is None:
            raise BadRequestException(code="DESTINATION_WAREHOUSE_REQUIRED", message="Warehouse tujuan wajib untuk transaksi masuk.")
        if payload.transaction_type in OUTBOUND_TRANSACTION_TYPES and source_warehouse is None:
            raise BadRequestException(code="SOURCE_WAREHOUSE_REQUIRED", message="Warehouse sumber wajib untuk transaksi keluar.")
        if payload.transaction_type in TRANSFER_TRANSACTION_TYPES:
            if source_warehouse is None or destination_warehouse is None:
                raise BadRequestException(code="WAREHOUSE_TRANSFER_INCOMPLETE", message="Warehouse sumber dan tujuan wajib untuk transfer internal.")
            if source_warehouse.id == destination_warehouse.id:
                raise BadRequestException(code="WAREHOUSE_TRANSFER_SAME_LOCATION", message="Warehouse sumber dan tujuan tidak boleh sama.")

        if source_warehouse is not None and source_location is None:
            source_location = await self._get_or_create_root_location(source_warehouse.id)
        if destination_warehouse is not None and destination_location is None:
            destination_location = await self._get_or_create_root_location(destination_warehouse.id)

        batch = None
        if batch_id is not None:
            batch = await self.batch_repository.get_by_id(batch_id)
            if batch is None or batch.tenant_id != tenant_id or batch.product_id != product_id:
                raise NotFoundException(code="INVENTORY_BATCH_NOT_FOUND", message="Batch inventory tidak ditemukan.")
            if batch.is_blocked and payload.transaction_type in OUTBOUND_TRANSACTION_TYPES:
                raise BadRequestException(code="INVENTORY_BATCH_BLOCKED", message="Batch inventory terblokir dan tidak boleh dikeluarkan.")

        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            transaction_type=payload.transaction_type,
            reference_type=payload.reference_type,
            reference_id=reference_id,
            product_id=product_id,
            batch_id=batch_id,
            source_warehouse_id=source_warehouse_id,
            source_location_id=source_location.id if source_location else None,
            destination_warehouse_id=destination_warehouse_id,
            destination_location_id=destination_location.id if destination_location else None,
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
                location_id=destination_location.id if destination_location else None,
                product_id=product_id,
                quantity=payload.quantity,
                unit_cost=payload.unit_cost,
            )
            if batch is not None:
                batch.warehouse_id = destination_warehouse_id
                batch.location_id = destination_location.id if destination_location else None
                batch.quantity_on_hand += payload.quantity
                batch.quantity_available = batch.quantity_on_hand - batch.quantity_reserved
        elif payload.transaction_type in OUTBOUND_TRANSACTION_TYPES:
            await self._decrease_balance(warehouse_id=source_warehouse_id, product_id=product_id, quantity=payload.quantity)
            if batch is not None:
                if batch.quantity_available < payload.quantity:
                    raise BadRequestException(code="INSUFFICIENT_BATCH_STOCK", message="Stok batch tersedia tidak cukup.")
                batch.quantity_on_hand -= payload.quantity
                batch.quantity_available = batch.quantity_on_hand - batch.quantity_reserved
        else:
            await self._decrease_balance(warehouse_id=source_warehouse_id, product_id=product_id, quantity=payload.quantity)
            await self._increase_balance(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                warehouse_id=destination_warehouse_id,
                location_id=destination_location.id if destination_location else None,
                product_id=product_id,
                quantity=payload.quantity,
                unit_cost=payload.unit_cost,
            )
            if batch is not None:
                batch.warehouse_id = destination_warehouse_id
                batch.location_id = destination_location.id if destination_location else None

        return transaction

    async def record_reserved_issue_transaction(self, payload: InventoryTransactionCreate, actor: User) -> InventoryTransaction:
        if payload.transaction_type != "ISSUE_TO_PRODUCTION":
            raise BadRequestException(
                code="INVALID_RESERVED_ISSUE_TRANSACTION_TYPE",
                message="Reserved issue hanya mendukung ISSUE_TO_PRODUCTION.",
            )
        return await self.create_transaction(payload, actor)

    async def _validate_warehouse(self, warehouse_id: UUID | None, tenant_id: UUID, not_found_message: str):
        if warehouse_id is None:
            return None
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if warehouse is None or warehouse.tenant_id != tenant_id:
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message=not_found_message)
        return warehouse

    async def _validate_location(self, location_id: UUID | None, warehouse_id: UUID | None, tenant_id: UUID, not_found_message: str):
        if location_id is None:
            return None
        location = await self.location_repository.get_by_id(location_id)
        if location is None or location.tenant_id != tenant_id or (warehouse_id is not None and location.warehouse_id != warehouse_id):
            raise NotFoundException(code="STOCK_LOCATION_NOT_FOUND", message=not_found_message)
        return location

    async def _get_or_create_root_location(self, warehouse_id: UUID) -> StockLocation:
        root = await self.location_repository.get_root_by_warehouse(warehouse_id)
        if root is not None:
            return root
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if warehouse is None:
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse tidak ditemukan untuk membuat root location.")
        root = StockLocation(
            tenant_id=warehouse.tenant_id,
            warehouse_id=warehouse.id,
            sppg_id=warehouse.sppg_id,
            parent_id=None,
            code=f"{warehouse.code}-ROOT",
            name=f"{warehouse.name} Root",
            location_type="WAREHOUSE",
            is_active=True,
        )
        return await self.location_repository.add(root)

    async def _increase_balance(
        self,
        *,
        tenant_id: UUID,
        sppg_id: UUID,
        warehouse_id: UUID | None,
        location_id: UUID | None,
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
                location_id=location_id,
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
        balance.location_id = location_id
        balance.quantity_available = new_quantity_on_hand - balance.quantity_reserved
        balance.average_cost = (current_total_cost + incoming_total_cost) / new_quantity_on_hand if new_quantity_on_hand > 0 else 0
        return balance

    async def _decrease_balance(self, *, warehouse_id: UUID | None, product_id: UUID, quantity: float) -> InventoryBalance:
        if warehouse_id is None:
            raise BadRequestException(code="SOURCE_WAREHOUSE_REQUIRED", message="Warehouse sumber wajib diisi.")
        balance = await self.balance_repository.get_by_warehouse_and_product(warehouse_id, product_id)
        if balance is None or balance.quantity_available < quantity:
            raise BadRequestException(code="INSUFFICIENT_STOCK", message="Stok tersedia tidak cukup untuk memproses transaksi.")
        balance.quantity_on_hand -= quantity
        balance.quantity_available = balance.quantity_on_hand - balance.quantity_reserved
        return balance
