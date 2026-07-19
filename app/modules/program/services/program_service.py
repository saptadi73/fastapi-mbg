from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.program.models.program import Program
from app.modules.program.models.program_period import ProgramPeriod
from app.modules.program.models.program_sppg import ProgramSppg
from app.modules.program.models.program_tenant import ProgramTenant
from app.modules.program.repositories.program_repository import ProgramRepository
from app.modules.program.schemas.program_schema import (
    ProgramCreate,
    ProgramPeriodCreate,
    ProgramSppgAssignmentCreate,
    ProgramTenantAssignmentCreate,
)
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class ProgramService:
    def __init__(
        self,
        repository: ProgramRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_tenant_scope(self) -> UUID | None:
        return self._parse_scope_uuid(
            get_current_tenant(),
            "INVALID_TENANT_CONTEXT",
            "Header X-Tenant-ID tidak valid.",
        )

    def _get_sppg_scope(self) -> UUID | None:
        return self._parse_scope_uuid(
            get_current_sppg(),
            "INVALID_SPPG_CONTEXT",
            "Header X-SPPG-ID tidak valid.",
        )

    async def list_programs(self) -> list[Program]:
        return await self.repository.list_programs(
            tenant_id=self._get_tenant_scope(),
            sppg_id=self._get_sppg_scope(),
        )

    async def get_program_bundle(self, program_id: UUID) -> dict:
        program = await self.repository.get_program_by_id(program_id)
        if program is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")

        tenant_scope = self._get_tenant_scope()
        sppg_scope = self._get_sppg_scope()
        if tenant_scope is not None and await self.repository.get_program_tenant(program_id, tenant_scope) is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")
        if sppg_scope is not None and await self.repository.get_program_sppg(program_id, sppg_scope) is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")

        return {
            "program": program,
            "periods": await self.repository.list_periods(program_id),
            "tenant_assignments": await self.repository.list_tenant_assignments(program_id),
            "sppg_assignments": await self.repository.list_sppg_assignments(program_id),
        }

    async def create_program(self, payload: ProgramCreate) -> Program:
        if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
            raise BadRequestException(
                code="INVALID_PROGRAM_DATE_RANGE",
                message="Tanggal akhir program tidak valid.",
            )
        existing = await self.repository.get_program_by_code(payload.code)
        if existing is not None:
            raise ConflictException(
                code="PROGRAM_CODE_ALREADY_EXISTS",
                message="Kode program sudah digunakan.",
            )
        return await self.repository.add_program(
            Program(
                code=payload.code,
                name=payload.name,
                description=payload.description,
                program_type=payload.program_type,
                funding_source_name=payload.funding_source_name,
                start_date=payload.start_date,
                end_date=payload.end_date,
                status=payload.status,
                is_active=payload.is_active,
            )
        )

    async def create_program_period(self, program_id: UUID, payload: ProgramPeriodCreate) -> ProgramPeriod:
        program = await self.repository.get_program_by_id(program_id)
        if program is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")
        if payload.date_end < payload.date_start:
            raise BadRequestException(
                code="INVALID_PROGRAM_PERIOD_DATE_RANGE",
                message="Tanggal akhir periode program tidak valid.",
            )
        if program.start_date and payload.date_start < program.start_date:
            raise BadRequestException(
                code="PROGRAM_PERIOD_BEFORE_PROGRAM_START",
                message="Tanggal mulai periode berada sebelum tanggal mulai program.",
            )
        if program.end_date and payload.date_end > program.end_date:
            raise BadRequestException(
                code="PROGRAM_PERIOD_AFTER_PROGRAM_END",
                message="Tanggal akhir periode berada setelah tanggal akhir program.",
            )
        existing = await self.repository.get_period_by_program_and_code(program_id, payload.code)
        if existing is not None:
            raise ConflictException(
                code="PROGRAM_PERIOD_CODE_ALREADY_EXISTS",
                message="Kode periode program sudah digunakan.",
            )
        return await self.repository.add_period(
            ProgramPeriod(
                program_id=program_id,
                code=payload.code,
                name=payload.name,
                date_start=payload.date_start,
                date_end=payload.date_end,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def assign_tenant(self, program_id: UUID, payload: ProgramTenantAssignmentCreate) -> ProgramTenant:
        program = await self.repository.get_program_by_id(program_id)
        if program is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
            raise BadRequestException(
                code="INVALID_PROGRAM_TENANT_DATE_RANGE",
                message="Tanggal assignment tenant program tidak valid.",
            )
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant tidak ditemukan.")
        existing = await self.repository.get_program_tenant(program_id, tenant_id)
        if existing is not None:
            raise ConflictException(
                code="PROGRAM_TENANT_ALREADY_ASSIGNED",
                message="Tenant sudah terhubung dengan program ini.",
            )
        return await self.repository.add_program_tenant(
            ProgramTenant(
                program_id=program_id,
                tenant_id=tenant_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def assign_sppg(self, program_id: UUID, payload: ProgramSppgAssignmentCreate) -> ProgramSppg:
        program = await self.repository.get_program_by_id(program_id)
        if program is None:
            raise NotFoundException(code="PROGRAM_NOT_FOUND", message="Program tidak ditemukan.")
        sppg_id = UUID(payload.sppg_id)
        enforce_sppg_write_scope(sppg_id)
        if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
            raise BadRequestException(
                code="INVALID_PROGRAM_SPPG_DATE_RANGE",
                message="Tanggal assignment SPPG program tidak valid.",
            )
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG tidak ditemukan.")
        tenant_id = UUID(payload.tenant_id) if payload.tenant_id else sppg.tenant_id
        if tenant_id != sppg.tenant_id:
            raise BadRequestException(
                code="PROGRAM_SPPG_TENANT_MISMATCH",
                message="Tenant assignment SPPG tidak sesuai dengan tenant pemilik SPPG.",
            )
        enforce_tenant_write_scope(tenant_id)
        if await self.repository.get_program_tenant(program_id, tenant_id) is None:
            raise BadRequestException(
                code="PROGRAM_TENANT_ASSIGNMENT_REQUIRED",
                message="Tenant pemilik SPPG harus diassign ke program terlebih dahulu.",
            )
        existing = await self.repository.get_program_sppg(program_id, sppg_id)
        if existing is not None:
            raise ConflictException(
                code="PROGRAM_SPPG_ALREADY_ASSIGNED",
                message="SPPG sudah terhubung dengan program ini.",
            )
        return await self.repository.add_program_sppg(
            ProgramSppg(
                program_id=program_id,
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )
