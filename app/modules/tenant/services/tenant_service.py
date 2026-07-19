from uuid import UUID

from app.modules.tenant.models.tenant import Tenant
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.tenant.schemas.tenant_schema import TenantCreate
from app.support.exceptions.base import ConflictException, NotFoundException


class TenantService:
    def __init__(self, repository: TenantRepository) -> None:
        self.repository = repository

    async def list_tenants(self) -> list[Tenant]:
        return await self.repository.list_all()

    async def get_tenant(self, tenant_id: UUID) -> Tenant:
        tenant = await self.repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(
                code="TENANT_NOT_FOUND",
                message="Tenant tidak ditemukan.",
            )
        return tenant

    async def create_tenant(self, payload: TenantCreate) -> Tenant:
        existing = await self.repository.get_by_code(payload.code)
        if existing is not None:
            raise ConflictException(
                code="TENANT_CODE_ALREADY_EXISTS",
                message="Kode tenant sudah digunakan.",
            )

        tenant = Tenant(
            code=payload.code,
            name=payload.name,
            is_active=payload.is_active,
        )
        return await self.repository.add(tenant)
