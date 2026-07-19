from uuid import UUID

from geoalchemy2.elements import WKTElement

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.geography.models.school import School
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.geography.schemas.school_schema import SchoolCreate
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class SchoolService:
    def __init__(
        self,
        repository: SchoolRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository

    async def list_schools(self) -> list[School]:
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

    async def get_school(self, school_id: UUID) -> School:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            school = await self.repository.get_by_id(school_id)
        else:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_TENANT_CONTEXT",
                    message="Header X-Tenant-ID tidak valid.",
                ) from exc
            school = await self.repository.get_by_id_and_tenant(school_id, tenant_id)
        if school is None:
            raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah tidak ditemukan.")
        return school

    async def create_school(self, payload: SchoolCreate) -> School:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(
                code="TENANT_NOT_FOUND",
                message="Tenant untuk sekolah tidak ditemukan.",
            )

        existing = await self.repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(
                code="SCHOOL_CODE_ALREADY_EXISTS",
                message="Kode sekolah sudah digunakan pada tenant ini.",
            )

        school = School(
            tenant_id=tenant.id,
            code=payload.code,
            name=payload.name,
            school_level=payload.school_level,
            address=payload.address,
            latitude=payload.latitude,
            longitude=payload.longitude,
            location=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326),
            student_count=payload.student_count,
            active_beneficiary_count=0,
        )
        return await self.repository.add(school)
