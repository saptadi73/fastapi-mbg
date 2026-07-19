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
from app.modules.funding.repositories.funding_repository import FundingRepository
from app.modules.funding.schemas.funding_schema import (
    FundingAgreementBundleRead,
    FundingAgreementCreate,
    FundingAgreementRead,
    FundingDisbursementCreate,
    FundingDisbursementRead,
    FundingRepaymentCreate,
    FundingRepaymentRead,
    FundingSourceCreate,
    FundingSourceRead,
    FundingSummaryRead,
)
from app.modules.funding.services.funding_service import FundingService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_funding_service(session: AsyncSession = Depends(get_db_session)) -> FundingService:
    return FundingService(
        FundingRepository(session),
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


@router.get("/sources")
async def list_funding_sources(request: Request, service: FundingService = Depends(get_funding_service)) -> dict:
    items = [FundingSourceRead.model_validate(item) for item in await service.list_sources()]
    return success_response(
        code="FUNDING_SOURCE_LIST_FOUND",
        message="Daftar funding source berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/sources", status_code=status.HTTP_201_CREATED)
async def create_funding_source(
    payload: FundingSourceCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_funding_service(session)
    source = await service.create_source(payload)
    await get_audit_service(session).record_event(
        event_type="FUNDING",
        module_name="funding",
        action_name="CREATE_SOURCE",
        summary="Funding source dibuat.",
        actor=actor,
        tenant_id=source.tenant_id,
        entity_type="funding_source",
        entity_id=source.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": source.code, "source_type": source.source_type},
    )
    await session.commit()
    return success_response(
        code="FUNDING_SOURCE_CREATED",
        message="Funding source berhasil dibuat.",
        data=FundingSourceRead.model_validate(source),
        meta={"request_id": request.state.request_id},
    )


@router.get("/agreements")
async def list_funding_agreements(request: Request, service: FundingService = Depends(get_funding_service)) -> dict:
    items = [FundingAgreementRead.model_validate(item) for item in await service.list_agreements()]
    return success_response(
        code="FUNDING_AGREEMENT_LIST_FOUND",
        message="Daftar funding agreement berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/agreements/{agreement_id}")
async def get_funding_agreement(
    agreement_id: UUID,
    request: Request,
    service: FundingService = Depends(get_funding_service),
) -> dict:
    bundle = await service.get_agreement_bundle(agreement_id)
    return success_response(
        code="FUNDING_AGREEMENT_FOUND",
        message="Detail funding agreement berhasil diambil.",
        data=FundingAgreementBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/agreements", status_code=status.HTTP_201_CREATED)
async def create_funding_agreement(
    payload: FundingAgreementCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_funding_service(session)
    agreement = await service.create_agreement(payload)
    await get_audit_service(session).record_event(
        event_type="FUNDING",
        module_name="funding",
        action_name="CREATE_AGREEMENT",
        summary="Funding agreement dibuat.",
        actor=actor,
        tenant_id=agreement.tenant_id,
        entity_type="funding_agreement",
        entity_id=agreement.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"agreement_type": agreement.agreement_type, "principal_amount": agreement.principal_amount},
    )
    await session.commit()
    return success_response(
        code="FUNDING_AGREEMENT_CREATED",
        message="Funding agreement berhasil dibuat.",
        data=FundingAgreementRead.model_validate(agreement),
        meta={"request_id": request.state.request_id},
    )


@router.get("/disbursements")
async def list_funding_disbursements(request: Request, service: FundingService = Depends(get_funding_service)) -> dict:
    items = [FundingDisbursementRead.model_validate(item) for item in await service.list_disbursements()]
    return success_response(
        code="FUNDING_DISBURSEMENT_LIST_FOUND",
        message="Daftar funding disbursement berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/agreements/{agreement_id}/disbursements", status_code=status.HTTP_201_CREATED)
async def create_funding_disbursement(
    agreement_id: UUID,
    payload: FundingDisbursementCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_funding_service(session)
    result = await service.create_disbursement(agreement_id, payload, actor)
    disbursement = result["disbursement"]
    await get_audit_service(session).record_event(
        event_type="FUNDING",
        module_name="funding",
        action_name="CREATE_DISBURSEMENT",
        summary="Funding disbursement dicatat.",
        actor=actor,
        tenant_id=disbursement.tenant_id,
        sppg_id=disbursement.sppg_id,
        entity_type="funding_disbursement",
        entity_id=disbursement.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"amount": disbursement.amount, "reference_number": disbursement.reference_number},
    )
    await session.commit()
    return success_response(
        code="FUNDING_DISBURSEMENT_CREATED",
        message="Funding disbursement berhasil dicatat.",
        data=FundingDisbursementRead.model_validate(disbursement),
        meta={"request_id": request.state.request_id},
    )


@router.get("/repayments")
async def list_funding_repayments(request: Request, service: FundingService = Depends(get_funding_service)) -> dict:
    items = [FundingRepaymentRead.model_validate(item) for item in await service.list_repayments()]
    return success_response(
        code="FUNDING_REPAYMENT_LIST_FOUND",
        message="Daftar funding repayment berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/agreements/{agreement_id}/repayments", status_code=status.HTTP_201_CREATED)
async def create_funding_repayment(
    agreement_id: UUID,
    payload: FundingRepaymentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_funding_service(session)
    result = await service.create_repayment(agreement_id, payload, actor)
    repayment = result["repayment"]
    await get_audit_service(session).record_event(
        event_type="FUNDING",
        module_name="funding",
        action_name="CREATE_REPAYMENT",
        summary="Funding repayment dicatat.",
        actor=actor,
        tenant_id=repayment.tenant_id,
        entity_type="funding_repayment",
        entity_id=repayment.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"principal_amount": repayment.principal_amount, "margin_amount": repayment.margin_amount},
    )
    await session.commit()
    return success_response(
        code="FUNDING_REPAYMENT_CREATED",
        message="Funding repayment berhasil dicatat.",
        data=FundingRepaymentRead.model_validate(repayment),
        meta={"request_id": request.state.request_id},
    )


@router.get("/summary")
async def get_funding_summary(request: Request, service: FundingService = Depends(get_funding_service)) -> dict:
    payload = await service.summary()
    return success_response(
        code="FUNDING_SUMMARY_FOUND",
        message="Ringkasan funding berhasil diambil.",
        data=FundingSummaryRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )
