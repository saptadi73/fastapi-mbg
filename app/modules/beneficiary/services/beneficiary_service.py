from uuid import UUID

from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.beneficiary.models.beneficiary import Beneficiary
from app.modules.beneficiary.repositories.beneficiary_repository import BeneficiaryRepository
from app.modules.beneficiary.schemas.beneficiary_schema import BeneficiaryCreate
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import ConflictException, NotFoundException


class BeneficiaryService:
    def __init__(
        self,
        repository: BeneficiaryRepository,
        tenant_repository: TenantRepository,
        school_repository: SchoolRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.school_repository = school_repository

    async def list_beneficiaries(self) -> list[Beneficiary]:
        return await self.repository.list_all()

    async def get_beneficiary(self, beneficiary_id: UUID) -> Beneficiary:
        beneficiary = await self.repository.get_by_id(beneficiary_id)
        if beneficiary is None:
            raise NotFoundException(
                code="BENEFICIARY_NOT_FOUND",
                message="Beneficiary tidak ditemukan.",
            )
        return beneficiary

    async def create_beneficiary(self, payload: BeneficiaryCreate) -> Beneficiary:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        school_id = UUID(payload.school_id)

        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(
                code="TENANT_NOT_FOUND",
                message="Tenant untuk beneficiary tidak ditemukan.",
            )

        school = await self.school_repository.get_by_id(school_id)
        if school is None or school.tenant_id != tenant_id:
            raise NotFoundException(
                code="SCHOOL_NOT_FOUND",
                message="Sekolah untuk beneficiary tidak ditemukan.",
            )

        existing = await self.repository.get_by_tenant_and_external_reference(
            tenant_id,
            payload.external_reference,
        )
        if existing is not None:
            raise ConflictException(
                code="BENEFICIARY_EXTERNAL_REFERENCE_ALREADY_EXISTS",
                message="External reference beneficiary sudah digunakan pada tenant ini.",
            )

        beneficiary = Beneficiary(
            tenant_id=tenant_id,
            school_id=school_id,
            external_reference=payload.external_reference,
            category=payload.category,
            age_group=payload.age_group,
            gender=payload.gender,
            dietary_restriction=payload.dietary_restriction,
            allergy_notes=payload.allergy_notes,
            is_active=payload.is_active,
        )
        return await self.repository.add(beneficiary)
