from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.document.repositories.document_repository import DocumentRepository
from app.modules.government_claim.repositories.government_claim_repository import GovernmentClaimRepository
from app.modules.government_claim.schemas.government_claim_schema import (
    ClaimAdjustmentCreate,
    ClaimAdjustmentRead,
    ClaimPaymentCreate,
    ClaimPaymentRead,
    ClaimSubmitPayload,
    ClaimVerificationCreate,
    ClaimVerificationRead,
    GovernmentClaimBundleRead,
    GovernmentClaimCreate,
    GovernmentClaimRead,
)
from app.modules.government_claim.services.government_claim_service import GovernmentClaimService
from app.modules.identity.models.user import User
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_government_claim_service(session: AsyncSession = Depends(get_db_session)) -> GovernmentClaimService:
    return GovernmentClaimService(
        GovernmentClaimRepository(session),
        DeliveryOrderRepository(session),
        ProductionOrderRepository(session),
        DocumentRepository(session),
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


@router.get("")
async def list_government_claims(request: Request, service: GovernmentClaimService = Depends(get_government_claim_service)) -> dict:
    items = [GovernmentClaimRead.model_validate(item) for item in await service.list_claims()]
    return success_response(
        code="GOVERNMENT_CLAIM_LIST_FOUND",
        message="Daftar government claim berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{claim_id}")
async def get_government_claim_detail(
    claim_id: UUID,
    request: Request,
    service: GovernmentClaimService = Depends(get_government_claim_service),
) -> dict:
    bundle = await service.get_claim_bundle(claim_id)
    return success_response(
        code="GOVERNMENT_CLAIM_FOUND",
        message="Detail government claim berhasil diambil.",
        data=GovernmentClaimBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_government_claim(
    payload: GovernmentClaimCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_government_claim_service(session)
    bundle = await service.create_claim(payload)
    claim = bundle["claim"]
    await get_audit_service(session).record_event(
        event_type="GOVERNMENT_CLAIM",
        module_name="government_claim",
        action_name="CREATE_CLAIM",
        summary="Government claim dibuat.",
        actor=actor,
        tenant_id=claim.tenant_id,
        sppg_id=claim.sppg_id,
        entity_type="government_claim",
        entity_id=claim.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"claim_number": claim.claim_number, "claimed_amount": claim.claimed_amount},
    )
    await session.commit()
    return success_response(
        code="GOVERNMENT_CLAIM_CREATED",
        message="Government claim berhasil dibuat.",
        data=GovernmentClaimBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{claim_id}/submit")
async def submit_government_claim(
    claim_id: UUID,
    payload: ClaimSubmitPayload,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_government_claim_service(session)
    claim = await service.submit_claim(claim_id, payload)
    await get_audit_service(session).record_event(
        event_type="GOVERNMENT_CLAIM",
        module_name="government_claim",
        action_name="SUBMIT_CLAIM",
        summary="Government claim disubmit.",
        actor=actor,
        tenant_id=claim.tenant_id,
        sppg_id=claim.sppg_id,
        entity_type="government_claim",
        entity_id=claim.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"submitted_at": str(payload.submitted_at)},
    )
    await session.commit()
    return success_response(
        code="GOVERNMENT_CLAIM_SUBMITTED",
        message="Government claim berhasil disubmit.",
        data=GovernmentClaimRead.model_validate(claim),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{claim_id}/verify")
async def verify_government_claim(
    claim_id: UUID,
    payload: ClaimVerificationCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_government_claim_service(session)
    result = await service.verify_claim(claim_id, payload)
    claim = result["claim"]
    verification = result["verification"]
    await get_audit_service(session).record_event(
        event_type="GOVERNMENT_CLAIM",
        module_name="government_claim",
        action_name="VERIFY_CLAIM",
        summary="Government claim diverifikasi.",
        actor=actor,
        tenant_id=claim.tenant_id,
        sppg_id=claim.sppg_id,
        entity_type="claim_verification",
        entity_id=verification.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"verification_status": verification.verification_status, "verified_amount": verification.verified_amount},
    )
    await session.commit()
    return success_response(
        code="GOVERNMENT_CLAIM_VERIFIED",
        message="Government claim berhasil diverifikasi.",
        data={
            "claim": GovernmentClaimRead.model_validate(claim),
            "verification": ClaimVerificationRead.model_validate(verification),
        },
        meta={"request_id": request.state.request_id},
    )


@router.post("/{claim_id}/adjustments", status_code=status.HTTP_201_CREATED)
async def add_claim_adjustment(
    claim_id: UUID,
    payload: ClaimAdjustmentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_government_claim_service(session)
    adjustment = await service.add_adjustment(claim_id, payload)
    await get_audit_service(session).record_event(
        event_type="GOVERNMENT_CLAIM",
        module_name="government_claim",
        action_name="ADD_ADJUSTMENT",
        summary="Adjustment government claim ditambahkan.",
        actor=actor,
        tenant_id=adjustment.tenant_id,
        entity_type="claim_adjustment",
        entity_id=adjustment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"adjustment_amount": adjustment.adjustment_amount},
    )
    await session.commit()
    return success_response(
        code="GOVERNMENT_CLAIM_ADJUSTMENT_CREATED",
        message="Adjustment government claim berhasil ditambahkan.",
        data=ClaimAdjustmentRead.model_validate(adjustment),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{claim_id}/payments", status_code=status.HTTP_201_CREATED)
async def add_claim_payment(
    claim_id: UUID,
    payload: ClaimPaymentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_government_claim_service(session)
    result = await service.record_payment(claim_id, payload, actor)
    payment = result["payment"]
    claim = result["claim"]
    await get_audit_service(session).record_event(
        event_type="GOVERNMENT_CLAIM",
        module_name="government_claim",
        action_name="RECORD_PAYMENT",
        summary="Pembayaran government claim dicatat.",
        actor=actor,
        tenant_id=claim.tenant_id,
        sppg_id=claim.sppg_id,
        entity_type="claim_payment",
        entity_id=payment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"amount": payment.amount, "journal_entry_id": str(payment.journal_entry_id)},
    )
    await session.commit()
    return success_response(
        code="GOVERNMENT_CLAIM_PAYMENT_RECORDED",
        message="Pembayaran government claim berhasil dicatat.",
        data={
            "claim": GovernmentClaimRead.model_validate(claim),
            "payment": ClaimPaymentRead.model_validate(payment),
        },
        meta={"request_id": request.state.request_id},
    )
