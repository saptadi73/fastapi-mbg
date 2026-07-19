from uuid import UUID

from app.modules.geography.models.school import School
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.geography.schemas.school_schema import SchoolCreate
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import ConflictException, NotFoundException


class SchoolService:
    def __init__(
        self,
        repository: SchoolRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository

    async def list_schools(self) -> list[School]:
        return await self.repository.list_all()

    async def get_school(self, school_id: UUID) -> School:
        school = await self.repository.get_by_id(school_id)
        if school is None:
            raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah tidak ditemukan.")
        return school

    async def create_school(self, payload: SchoolCreate) -> School:
        tenant_id = UUID(payload.tenant_id)
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
            student_count=payload.student_count,
            active_beneficiary_count=0,
        )
        return await self.repository.add(school)
