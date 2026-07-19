from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.warehouse_schema import WarehouseCreate
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class WarehouseService:
    def __init__(
        self,
        repository: WarehouseRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository

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

    async def list_warehouses(self) -> list[Warehouse]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_warehouse(self, warehouse_id: UUID) -> Warehouse:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            warehouse = await self.repository.get_by_id(warehouse_id)
        else:
            warehouse = await self.repository.get_by_id_and_scope(
                warehouse_id,
                tenant_id=tenant_id,
                sppg_id=sppg_id,
            )
        if warehouse is None:
            raise NotFoundException(code="WAREHOUSE_NOT_FOUND", message="Warehouse tidak ditemukan.")
        return warehouse

    async def create_warehouse(self, payload: WarehouseCreate) -> Warehouse:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk warehouse tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG untuk warehouse tidak ditemukan.")
        existing = await self.repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(
                code="WAREHOUSE_CODE_ALREADY_EXISTS",
                message="Kode warehouse sudah digunakan pada tenant ini.",
            )
        warehouse = Warehouse(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            code=payload.code,
            name=payload.name,
            warehouse_type=payload.warehouse_type,
            location=payload.location,
            is_active=payload.is_active,
        )
        return await self.repository.add(warehouse)
