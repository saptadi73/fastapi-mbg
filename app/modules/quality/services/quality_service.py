from datetime import datetime
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.quality.models.qc_inspection import QCInspection
from app.modules.quality.models.qc_inspection_line import QCInspectionLine
from app.modules.quality.repositories.qc_inspection_repository import QCInspectionRepository
from app.modules.quality.schemas.quality_schema import QCInspectionCreate, QCInspectionLineCreate
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException

QC_STATUS_DRAFT = "DRAFT"
QC_STATUS_PASSED = "PASSED"
QC_STATUS_FAILED = "FAILED"


class QualityService:
    def __init__(
        self,
        repository: QCInspectionRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        production_order_repository: ProductionOrderRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.production_order_repository = production_order_repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def list_inspections(self) -> list[QCInspection]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_inspection(self, inspection_id: UUID) -> QCInspection:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            inspection = await self.repository.get_by_id(inspection_id)
        else:
            inspection = await self.repository.get_by_id_and_scope(inspection_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if inspection is None:
            raise NotFoundException(code="QC_INSPECTION_NOT_FOUND", message="Inspeksi QC tidak ditemukan.")
        return inspection

    async def get_inspection_bundle(self, inspection_id: UUID) -> dict:
        inspection = await self.get_inspection(inspection_id)
        lines = await self.repository.list_lines(inspection_id)
        return {"inspection": inspection, "lines": lines}

    async def create_inspection(self, payload: QCInspectionCreate) -> QCInspection:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        reference_id = UUID(payload.reference_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant QC tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG QC tidak ditemukan.")
        if payload.reference_type == "PRODUCTION_ORDER":
            production_order = await self.production_order_repository.get_by_id(reference_id)
            if production_order is None or production_order.tenant_id != tenant_id or production_order.sppg_id != sppg_id:
                raise NotFoundException(
                    code="PRODUCTION_ORDER_NOT_FOUND",
                    message="Production order referensi QC tidak ditemukan.",
                )
        next_number = await self.repository.count_by_tenant(tenant_id) + 1
        return await self.repository.add(
            QCInspection(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                inspection_number=f"QC-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                inspection_type=payload.inspection_type,
                stage=payload.stage,
                reference_type=payload.reference_type,
                reference_id=reference_id,
                inspection_at=payload.inspection_at,
                inspector_name=payload.inspector_name,
                status=QC_STATUS_DRAFT,
                overall_result=None,
                is_mandatory_for_release=payload.is_mandatory_for_release,
                notes=payload.notes,
            )
        )

    async def add_inspection_line(self, inspection_id: UUID, payload: QCInspectionLineCreate) -> QCInspectionLine:
        inspection = await self.get_inspection(inspection_id)
        if inspection.status in {QC_STATUS_PASSED, QC_STATUS_FAILED}:
            raise BadRequestException(
                code="QC_INSPECTION_ALREADY_FINALIZED",
                message="Inspeksi QC yang sudah final tidak bisa ditambah line lagi.",
            )
        result_status = payload.result_status.upper()
        if result_status not in {"PASS", "FAIL"}:
            raise BadRequestException(
                code="QC_RESULT_STATUS_INVALID",
                message="Result status QC hanya boleh PASS atau FAIL.",
            )
        return await self.repository.add_line(
            QCInspectionLine(
                tenant_id=inspection.tenant_id,
                inspection_id=inspection.id,
                parameter_name=payload.parameter_name,
                expected_value=payload.expected_value,
                actual_value=payload.actual_value,
                result_status=result_status,
                notes=payload.notes,
            )
        )

    async def finalize_inspection(self, inspection_id: UUID) -> dict:
        inspection = await self.get_inspection(inspection_id)
        lines = await self.repository.list_lines(inspection_id)
        if not lines:
            raise BadRequestException(
                code="QC_INSPECTION_LINES_REQUIRED",
                message="Inspeksi QC harus memiliki minimal satu line sebelum difinalisasi.",
            )
        inspection.status = QC_STATUS_FAILED if any(line.result_status == "FAIL" for line in lines) else QC_STATUS_PASSED
        inspection.overall_result = inspection.status
        return {"inspection": inspection, "lines": lines}

    async def validate_release_for_reference(self, reference_type: str, reference_id: UUID) -> None:
        inspections = await self.repository.list_mandatory_by_reference(reference_type, reference_id)
        if not inspections:
            return
        if any(item.status != QC_STATUS_PASSED for item in inspections):
            raise BadRequestException(
                code="PRODUCTION_QC_RELEASE_BLOCKED",
                message="Production order belum lolos QC wajib sehingga belum dapat dilepas ke delivery.",
            )
