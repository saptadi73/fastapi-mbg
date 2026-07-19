from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.feedback.repositories.feedback_repository import FeedbackRepository
from app.modules.feedback.schemas.feedback_schema import (
    ComplaintCreate,
    ComplaintRead,
    FeedbackSubmissionBundleRead,
    FeedbackSubmissionCreate,
    FeedbackSubmissionRead,
    FeedbackSummaryRead,
    ServiceQualityScoreCreate,
    ServiceQualityScoreRead,
)
from app.modules.feedback.services.feedback_service import FeedbackService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.identity.models.user import User
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_feedback_service(session: AsyncSession = Depends(get_db_session)) -> FeedbackService:
    return FeedbackService(
        FeedbackRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        SchoolRepository(session),
        MealPlanRepository(session),
        DeliveryOrderRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/submissions")
async def list_submissions(request: Request, service: FeedbackService = Depends(get_feedback_service)) -> dict:
    items = [FeedbackSubmissionRead.model_validate(item) for item in await service.list_submissions()]
    return success_response(
        code="FEEDBACK_SUBMISSION_LIST_FOUND",
        message="Daftar feedback submission berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/submissions/{submission_id}")
async def get_submission_detail(
    submission_id: UUID,
    request: Request,
    service: FeedbackService = Depends(get_feedback_service),
) -> dict:
    bundle = await service.get_submission_bundle(submission_id)
    return success_response(
        code="FEEDBACK_SUBMISSION_FOUND",
        message="Detail feedback submission berhasil diambil.",
        data=FeedbackSubmissionBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/submissions", status_code=status.HTTP_201_CREATED)
async def create_submission(
    payload: FeedbackSubmissionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "delivery_officer")),
) -> dict:
    service = get_feedback_service(session)
    bundle = await service.create_submission(payload)
    submission = bundle["submission"]
    await get_audit_service(session).record_event(
        event_type="FEEDBACK",
        module_name="feedback",
        action_name="CREATE_FEEDBACK_SUBMISSION",
        summary="Feedback submission dibuat.",
        actor=actor,
        tenant_id=submission.tenant_id,
        sppg_id=submission.sppg_id,
        entity_type="feedback_submission",
        entity_id=submission.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"source_type": submission.source_type, "status": submission.status},
    )
    await session.commit()
    return success_response(
        code="FEEDBACK_SUBMISSION_CREATED",
        message="Feedback submission berhasil dibuat.",
        data=FeedbackSubmissionBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.get("/complaints")
async def list_complaints(request: Request, service: FeedbackService = Depends(get_feedback_service)) -> dict:
    items = [ComplaintRead.model_validate(item) for item in await service.list_complaints()]
    return success_response(
        code="COMPLAINT_LIST_FOUND",
        message="Daftar complaint berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/complaints", status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "delivery_officer")),
) -> dict:
    service = get_feedback_service(session)
    complaint = await service.create_complaint(payload)
    await get_audit_service(session).record_event(
        event_type="FEEDBACK",
        module_name="feedback",
        action_name="CREATE_COMPLAINT",
        summary="Complaint feedback dicatat.",
        actor=actor,
        tenant_id=complaint.tenant_id,
        sppg_id=complaint.sppg_id,
        entity_type="complaint",
        entity_id=complaint.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"category": complaint.category, "severity": complaint.severity},
    )
    await session.commit()
    return success_response(
        code="COMPLAINT_CREATED",
        message="Complaint berhasil dicatat.",
        data=ComplaintRead.model_validate(complaint),
        meta={"request_id": request.state.request_id},
    )


@router.get("/service-quality-scores")
async def list_scores(request: Request, service: FeedbackService = Depends(get_feedback_service)) -> dict:
    items = [ServiceQualityScoreRead.model_validate(item) for item in await service.list_scores()]
    return success_response(
        code="SERVICE_QUALITY_SCORE_LIST_FOUND",
        message="Daftar service quality score berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/service-quality-scores", status_code=status.HTTP_201_CREATED)
async def create_score(
    payload: ServiceQualityScoreCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer")),
) -> dict:
    service = get_feedback_service(session)
    score = await service.create_score(payload)
    await get_audit_service(session).record_event(
        event_type="FEEDBACK",
        module_name="feedback",
        action_name="CREATE_SERVICE_QUALITY_SCORE",
        summary="Service quality score dicatat.",
        actor=actor,
        tenant_id=score.tenant_id,
        sppg_id=score.sppg_id,
        entity_type="service_quality_score",
        entity_id=score.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"score_date": str(score.score_date), "total_score": score.total_score},
    )
    await session.commit()
    return success_response(
        code="SERVICE_QUALITY_SCORE_CREATED",
        message="Service quality score berhasil dicatat.",
        data=ServiceQualityScoreRead.model_validate(score),
        meta={"request_id": request.state.request_id},
    )


@router.get("/summary")
async def get_summary(request: Request, service: FeedbackService = Depends(get_feedback_service)) -> dict:
    payload = await service.summary()
    return success_response(
        code="FEEDBACK_SUMMARY_FOUND",
        message="Ringkasan feedback berhasil diambil.",
        data=FeedbackSummaryRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )
