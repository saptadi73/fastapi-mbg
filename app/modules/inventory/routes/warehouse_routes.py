from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.routes.stock_routes import INVENTORY_WRITE_ROLES
from app.modules.inventory.schemas.warehouse_schema import WarehouseCreate, WarehouseRead
from app.modules.inventory.services.warehouse_service import WarehouseService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter(prefix="/warehouses")


def get_warehouse_service(session: AsyncSession = Depends(get_db_session)) -> WarehouseService:
    return WarehouseService(
        WarehouseRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


@router.get("/")
async def list_warehouses(request: Request, service: WarehouseService = Depends(get_warehouse_service)) -> dict:
    items = [WarehouseRead.model_validate(item) for item in await service.list_warehouses()]
    return success_response(
        code="WAREHOUSE_LIST_FOUND",
        message="Daftar warehouse berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{warehouse_id}")
async def get_warehouse(
    warehouse_id: UUID,
    request: Request,
    service: WarehouseService = Depends(get_warehouse_service),
) -> dict:
    warehouse = await service.get_warehouse(warehouse_id)
    return success_response(
        code="WAREHOUSE_FOUND",
        message="Detail warehouse berhasil diambil.",
        data=WarehouseRead.model_validate(warehouse),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(*INVENTORY_WRITE_ROLES)),
) -> dict:
    service = WarehouseService(
        WarehouseRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )
    warehouse = await service.create_warehouse(payload)
    await session.commit()
    return success_response(
        code="WAREHOUSE_CREATED",
        message="Warehouse berhasil dibuat.",
        data=WarehouseRead.model_validate(warehouse),
        meta={"request_id": request.state.request_id},
    )
