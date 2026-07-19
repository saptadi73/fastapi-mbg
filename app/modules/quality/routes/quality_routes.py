from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.quality.repositories.qc_inspection_repository import QCInspectionRepository
from app.modules.quality.schemas.quality_schema import (
    QCInspectionBundleRead,
    QCInspectionCreate,
    QCInspectionLineCreate,
    QCInspectionLineRead,
    QCInspectionRead,
)
from app.modules.quality.services.quality_service import QualityService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter(prefix="/inspections")


def get_quality_service(session: AsyncSession = Depends(get_db_session)) -> QualityService:
    return QualityService(
        QCInspectionRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        ProductionOrderRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/")
async def list_qc_inspections(request: Request, service: QualityService = Depends(get_quality_service)) -> dict:
    items = [QCInspectionRead.model_validate(item) for item in await service.list_inspections()]
    return success_response(
        code="QC_INSPECTION_LIST_FOUND",
        message="Daftar inspeksi QC berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{inspection_id}")
async def get_qc_inspection(
    inspection_id: UUID,
    request: Request,
    service: QualityService = Depends(get_quality_service),
) -> dict:
    bundle = await service.get_inspection_bundle(inspection_id)
    return success_response(
        code="QC_INSPECTION_FOUND",
        message="Detail inspeksi QC berhasil diambil.",
        data=QCInspectionBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_qc_inspection(
    payload: QCInspectionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer")),
) -> dict:
    service = get_quality_service(session)
    inspection = await service.create_inspection(payload)
    await get_audit_service(session).record_event(
        event_type="QUALITY",
        module_name="quality",
        action_name="CREATE_INSPECTION",
        summary="Inspeksi QC dibuat.",
        actor=actor,
        tenant_id=inspection.tenant_id,
        sppg_id=inspection.sppg_id,
        entity_type="qc_inspection",
        entity_id=inspection.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"reference_type": payload.reference_type, "reference_id": payload.reference_id},
    )
    await session.commit()
    return success_response(
        code="QC_INSPECTION_CREATED",
        message="Inspeksi QC berhasil dibuat.",
        data=QCInspectionRead.model_validate(inspection),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{inspection_id}/lines", status_code=status.HTTP_201_CREATED)
async def add_qc_inspection_line(
    inspection_id: UUID,
    payload: QCInspectionLineCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer")),
) -> dict:
    service = get_quality_service(session)
    line = await service.add_inspection_line(inspection_id, payload)
    await get_audit_service(session).record_event(
        event_type="QUALITY",
        module_name="quality",
        action_name="ADD_INSPECTION_LINE",
        summary="Line inspeksi QC ditambahkan.",
        actor=actor,
        tenant_id=line.tenant_id,
        entity_type="qc_inspection_line",
        entity_id=line.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"result_status": payload.result_status, "parameter_name": payload.parameter_name},
    )
    await session.commit()
    return success_response(
        code="QC_INSPECTION_LINE_CREATED",
        message="Line inspeksi QC berhasil ditambahkan.",
        data=QCInspectionLineRead.model_validate(line),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{inspection_id}/finalize")
async def finalize_qc_inspection(
    inspection_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer")),
) -> dict:
    service = get_quality_service(session)
    bundle = await service.finalize_inspection(inspection_id)
    await get_audit_service(session).record_event(
        event_type="QUALITY",
        module_name="quality",
        action_name="FINALIZE_INSPECTION",
        summary="Inspeksi QC difinalisasi.",
        actor=actor,
        tenant_id=bundle["inspection"].tenant_id,
        sppg_id=bundle["inspection"].sppg_id,
        entity_type="qc_inspection",
        entity_id=bundle["inspection"].id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"status": bundle["inspection"].status, "line_count": len(bundle["lines"])},
    )
    await session.commit()
    return success_response(
        code="QC_INSPECTION_FINALIZED",
        message="Inspeksi QC berhasil difinalisasi.",
        data=QCInspectionBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )
