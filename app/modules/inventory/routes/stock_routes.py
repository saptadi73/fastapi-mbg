from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_schema import (
    InventoryBalanceRead,
    InventoryTransactionCreate,
    InventoryTransactionRead,
)
from app.modules.inventory.services.stock_service import StockService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.repositories.uom_repository import UomRepository
from app.support.responses.envelope import success_response

router = APIRouter()
INVENTORY_WRITE_ROLES = (
    "super_admin",
    "tenant_admin",
    "operations_manager",
    "warehouse_operator",
    "procurement_officer",
)


def get_stock_service(session: AsyncSession = Depends(get_db_session)) -> StockService:
    return StockService(
        InventoryTransactionRepository(session),
        InventoryBalanceRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        ProductRepository(session),
        UomRepository(session),
        WarehouseRepository(session),
    )


@router.get("/transactions/")
async def list_inventory_transactions(request: Request, service: StockService = Depends(get_stock_service)) -> dict:
    items = [InventoryTransactionRead.model_validate(item) for item in await service.list_transactions()]
    return success_response(
        code="INVENTORY_TRANSACTION_LIST_FOUND",
        message="Daftar transaksi inventory berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/transactions/", status_code=status.HTTP_201_CREATED)
async def create_inventory_transaction(
    payload: InventoryTransactionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles(*INVENTORY_WRITE_ROLES)),
) -> dict:
    service = get_stock_service(session)
    transaction = await service.create_transaction(payload, current_user)
    await session.commit()
    return success_response(
        code="INVENTORY_TRANSACTION_CREATED",
        message="Transaksi inventory berhasil diposting.",
        data=InventoryTransactionRead.model_validate(transaction),
        meta={"request_id": request.state.request_id},
    )


@router.get("/balances/")
async def list_inventory_balances(request: Request, service: StockService = Depends(get_stock_service)) -> dict:
    items = [InventoryBalanceRead.model_validate(item) for item in await service.list_balances()]
    return success_response(
        code="INVENTORY_BALANCE_LIST_FOUND",
        message="Daftar saldo inventory berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )
