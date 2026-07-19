from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.sppg.models.sppg import Sppg
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.sppg.schemas.sppg_schema import SppgCreate
from app.support.exceptions.base import BadRequestException
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import ConflictException, NotFoundException


class SppgService:
    def __init__(
        self,
        repository: SppgRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository

    async def list_sppg(self) -> list[Sppg]:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            return await self.repository.list_all()
        try:
            tenant_id = UUID(current_tenant)
        except ValueError as exc:
            raise BadRequestException(
                code="INVALID_TENANT_CONTEXT",
                message="Header X-Tenant-ID tidak valid.",
            ) from exc
        return await self.repository.list_all(tenant_id)

    async def get_sppg(self, sppg_id: UUID) -> Sppg:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            sppg = await self.repository.get_by_id(sppg_id)
        else:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_TENANT_CONTEXT",
                    message="Header X-Tenant-ID tidak valid.",
                ) from exc
            sppg = await self.repository.get_by_id_and_tenant(sppg_id, tenant_id)
        if sppg is None:
            raise NotFoundException(
                code="SPPG_NOT_FOUND",
                message="SPPG tidak ditemukan.",
            )
        return sppg

    async def create_sppg(self, payload: SppgCreate) -> Sppg:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(
                code="TENANT_NOT_FOUND",
                message="Tenant untuk SPPG tidak ditemukan.",
            )

        existing = await self.repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(
                code="SPPG_CODE_ALREADY_EXISTS",
                message="Kode SPPG sudah digunakan pada tenant ini.",
            )

        sppg = Sppg(
            tenant_id=tenant.id,
            code=payload.code,
            name=payload.name,
            address=payload.address,
            province=payload.province,
            city=payload.city,
            district=payload.district,
            village=payload.village,
            latitude=payload.latitude,
            longitude=payload.longitude,
            service_radius_meter=payload.service_radius_meter,
            timezone=payload.timezone,
            is_active=payload.is_active,
        )
        return await self.repository.add(sppg)
