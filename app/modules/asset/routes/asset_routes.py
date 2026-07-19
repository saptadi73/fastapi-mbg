from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.asset.repositories.asset_repository import AssetRepository
from app.modules.asset.schemas.asset_schema import (
    AssetAssignmentCreate,
    AssetAssignmentRead,
    AssetBundleRead,
    AssetCategoryCreate,
    AssetCategoryRead,
    AssetCreate,
    AssetDepreciationCreate,
    AssetDepreciationRead,
    AssetRead,
)
from app.modules.asset.services.asset_service import AssetService
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_asset_service(session: AsyncSession = Depends(get_db_session)) -> AssetService:
    return AssetService(
        AssetRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        AccountingService(
            AccountRepository(session),
            JournalEntryRepository(session),
            JournalLineRepository(session),
            TenantRepository(session),
        ),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/categories")
async def list_categories(request: Request, service: AssetService = Depends(get_asset_service)) -> dict:
    items = [AssetCategoryRead.model_validate(item) for item in await service.list_categories()]
    return success_response(
        code="ASSET_CATEGORY_LIST_FOUND",
        message="Daftar kategori asset berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: AssetCategoryCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager", "operations_manager")),
) -> dict:
    service = get_asset_service(session)
    category = await service.create_category(payload)
    await get_audit_service(session).record_event(
        event_type="ASSET",
        module_name="asset",
        action_name="CREATE_ASSET_CATEGORY",
        summary="Kategori asset dibuat.",
        actor=actor,
        tenant_id=category.tenant_id,
        entity_type="asset_category",
        entity_id=category.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": category.code},
    )
    await session.commit()
    return success_response(
        code="ASSET_CATEGORY_CREATED",
        message="Kategori asset berhasil dibuat.",
        data=AssetCategoryRead.model_validate(category),
        meta={"request_id": request.state.request_id},
    )


@router.get("/")
async def list_assets(request: Request, service: AssetService = Depends(get_asset_service)) -> dict:
    items = [AssetRead.model_validate(item) for item in await service.list_assets()]
    return success_response(
        code="ASSET_LIST_FOUND",
        message="Daftar asset berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager", "operations_manager")),
) -> dict:
    service = get_asset_service(session)
    asset = await service.create_asset(payload)
    await get_audit_service(session).record_event(
        event_type="ASSET",
        module_name="asset",
        action_name="CREATE_ASSET",
        summary="Asset dibuat.",
        actor=actor,
        tenant_id=asset.tenant_id,
        sppg_id=asset.sppg_id,
        entity_type="asset",
        entity_id=asset.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"asset_code": asset.asset_code},
    )
    await session.commit()
    return success_response(
        code="ASSET_CREATED",
        message="Asset berhasil dibuat.",
        data=AssetRead.model_validate(asset),
        meta={"request_id": request.state.request_id},
    )


@router.get("/assignments/")
async def list_assignments(request: Request, service: AssetService = Depends(get_asset_service)) -> dict:
    items = [AssetAssignmentRead.model_validate(item) for item in await service.list_assignments()]
    return success_response(
        code="ASSET_ASSIGNMENT_LIST_FOUND",
        message="Daftar assignment asset berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/{asset_id}/assignments", status_code=status.HTTP_201_CREATED)
async def assign_asset(
    asset_id: UUID,
    payload: AssetAssignmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_asset_service(session)
    assignment = await service.assign_asset(asset_id, payload)
    await get_audit_service(session).record_event(
        event_type="ASSET",
        module_name="asset",
        action_name="ASSIGN_ASSET",
        summary="Asset diassign ke SPPG.",
        actor=actor,
        tenant_id=assignment.tenant_id,
        sppg_id=assignment.sppg_id,
        entity_type="asset_assignment",
        entity_id=assignment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"assignment_role": assignment.assignment_role},
    )
    await session.commit()
    return success_response(
        code="ASSET_ASSIGNED",
        message="Assignment asset berhasil dibuat.",
        data=AssetAssignmentRead.model_validate(assignment),
        meta={"request_id": request.state.request_id},
    )


@router.get("/depreciations/")
async def list_depreciations(request: Request, service: AssetService = Depends(get_asset_service)) -> dict:
    items = [AssetDepreciationRead.model_validate(item) for item in await service.list_depreciations()]
    return success_response(
        code="ASSET_DEPRECIATION_LIST_FOUND",
        message="Daftar depresiasi asset berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/{asset_id}/depreciations", status_code=status.HTTP_201_CREATED)
async def create_depreciation(
    asset_id: UUID,
    payload: AssetDepreciationCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_asset_service(session)
    result = await service.create_depreciation(asset_id, payload, actor)
    depreciation = result["depreciation"]
    await get_audit_service(session).record_event(
        event_type="ASSET",
        module_name="asset",
        action_name="CREATE_ASSET_DEPRECIATION",
        summary="Depresiasi asset dicatat.",
        actor=actor,
        tenant_id=depreciation.tenant_id,
        sppg_id=depreciation.sppg_id,
        entity_type="asset_depreciation",
        entity_id=depreciation.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"depreciation_amount": depreciation.depreciation_amount},
    )
    await session.commit()
    return success_response(
        code="ASSET_DEPRECIATION_CREATED",
        message="Depresiasi asset berhasil dicatat.",
        data=AssetDepreciationRead.model_validate(depreciation),
        meta={"request_id": request.state.request_id},
    )


@router.get("/{asset_id}")
async def get_asset_detail(asset_id: UUID, request: Request, service: AssetService = Depends(get_asset_service)) -> dict:
    bundle = await service.get_asset_bundle(asset_id)
    return success_response(
        code="ASSET_FOUND",
        message="Detail asset berhasil diambil.",
        data=AssetBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )
