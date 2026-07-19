from uuid import UUID

from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.uom.models.uom import Uom
from app.modules.uom.repositories.uom_repository import UomRepository
from app.modules.uom.schemas.uom_schema import UomCreate
from app.support.exceptions.base import ConflictException, NotFoundException


class UomService:
    def __init__(self, repository: UomRepository, tenant_repository: TenantRepository) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository

    async def list_uoms(self) -> list[Uom]:
        return await self.repository.list_all()

    async def get_uom(self, uom_id: UUID) -> Uom:
        uom = await self.repository.get_by_id(uom_id)
        if uom is None:
            raise NotFoundException(code="UOM_NOT_FOUND", message="UoM tidak ditemukan.")
        return uom

    async def create_uom(self, payload: UomCreate) -> Uom:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk UoM tidak ditemukan.")
        existing = await self.repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(code="UOM_CODE_ALREADY_EXISTS", message="Kode UoM sudah digunakan pada tenant ini.")
        uom = Uom(
            tenant_id=tenant_id,
            code=payload.code,
            name=payload.name,
            symbol=payload.symbol,
            dimension=payload.dimension,
            factor_to_base=payload.factor_to_base,
            is_active=payload.is_active,
        )
        return await self.repository.add(uom)
