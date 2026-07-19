from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.stock_location_repository import StockLocationRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_schema import (
    FEFOIssuePreviewRead,
    FEFOIssuePreviewRequest,
    InventoryBatchCreate,
    InventoryBatchRead,
    InventoryBalanceRead,
    InventoryTransactionCreate,
    InventoryTransactionRead,
    StockLocationCreate,
    StockLocationRead,
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
        StockLocationRepository(session),
        InventoryBatchRepository(session),
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


@router.get("/locations/")
async def list_stock_locations(request: Request, service: StockService = Depends(get_stock_service)) -> dict:
    items = [StockLocationRead.model_validate(item) for item in await service.list_locations()]
    return success_response(
        code="STOCK_LOCATION_LIST_FOUND",
        message="Daftar stock location berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/locations/", status_code=status.HTTP_201_CREATED)
async def create_stock_location(
    payload: StockLocationCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(*INVENTORY_WRITE_ROLES)),
) -> dict:
    service = get_stock_service(session)
    location = await service.create_location(payload)
    await session.commit()
    return success_response(
        code="STOCK_LOCATION_CREATED",
        message="Stock location berhasil dibuat.",
        data=StockLocationRead.model_validate(location),
        meta={"request_id": request.state.request_id},
    )


@router.get("/batches/")
async def list_inventory_batches(request: Request, service: StockService = Depends(get_stock_service)) -> dict:
    items = [InventoryBatchRead.model_validate(item) for item in await service.list_batches()]
    return success_response(
        code="INVENTORY_BATCH_LIST_FOUND",
        message="Daftar batch inventory berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/batches/", status_code=status.HTTP_201_CREATED)
async def create_inventory_batch(
    payload: InventoryBatchCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(*INVENTORY_WRITE_ROLES)),
) -> dict:
    service = get_stock_service(session)
    batch = await service.create_batch(payload)
    await session.commit()
    return success_response(
        code="INVENTORY_BATCH_CREATED",
        message="Batch inventory berhasil dibuat.",
        data=InventoryBatchRead.model_validate(batch),
        meta={"request_id": request.state.request_id},
    )


@router.get("/expiry-alerts")
async def list_expiry_alerts(request: Request, days_ahead: int = 14, service: StockService = Depends(get_stock_service)) -> dict:
    items = [InventoryBatchRead.model_validate(item) for item in await service.list_expiry_alerts(days_ahead)]
    return success_response(
        code="INVENTORY_EXPIRY_ALERT_FOUND",
        message="Daftar batch mendekati expiry berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items), "days_ahead": days_ahead},
    )


@router.post("/issues/fefo-preview")
async def preview_fefo_issue(payload: FEFOIssuePreviewRequest, request: Request, service: StockService = Depends(get_stock_service)) -> dict:
    result = await service.suggest_fefo_issue(payload)
    return success_response(
        code="INVENTORY_FEFO_PREVIEW_FOUND",
        message="Preview FEFO berhasil dihitung.",
        data=FEFOIssuePreviewRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )
