from uuid import UUID

from app.modules.sppg.models.sppg import Sppg
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.sppg.schemas.sppg_schema import SppgCreate
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
        return await self.repository.list_all()

    async def get_sppg(self, sppg_id: UUID) -> Sppg:
        sppg = await self.repository.get_by_id(sppg_id)
        if sppg is None:
            raise NotFoundException(
                code="SPPG_NOT_FOUND",
                message="SPPG tidak ditemukan.",
            )
        return sppg

    async def create_sppg(self, payload: SppgCreate) -> Sppg:
        tenant_id = UUID(payload.tenant_id)
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
            city=payload.city,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        return await self.repository.add(sppg)
