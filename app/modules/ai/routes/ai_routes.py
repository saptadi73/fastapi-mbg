from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.ai.repositories.ai_repository import AIRepository
from app.modules.ai.schemas.ai_schema import (
    AIDailySummaryCreate,
    AIDailySummaryRead,
    AIForecastCreate,
    AIForecastRead,
    AIOverviewRead,
    AIRecommendationCreate,
    AIRecommendationRead,
)
from app.modules.ai.services.ai_service import AIService
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_ai_service(session: AsyncSession = Depends(get_db_session)) -> AIService:
    return AIService(
        AIRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/forecasts")
async def list_forecasts(request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    items = [AIForecastRead.model_validate(item) for item in await service.list_forecasts()]
    return success_response(
        code="AI_FORECAST_LIST_FOUND",
        message="Daftar AI forecast berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/forecasts", status_code=status.HTTP_201_CREATED)
async def create_forecast(
    payload: AIForecastCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "finance_manager")),
) -> dict:
    service = get_ai_service(session)
    forecast = await service.create_forecast(payload)
    await get_audit_service(session).record_event(
        event_type="AI",
        module_name="ai",
        action_name="CREATE_FORECAST",
        summary="AI forecast dibuat.",
        actor=actor,
        tenant_id=forecast.tenant_id,
        sppg_id=forecast.sppg_id,
        entity_type="ai_forecast",
        entity_id=forecast.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"forecast_type": forecast.forecast_type, "target_date": str(forecast.target_date)},
    )
    await session.commit()
    return success_response(
        code="AI_FORECAST_CREATED",
        message="AI forecast berhasil dibuat.",
        data=AIForecastRead.model_validate(forecast),
        meta={"request_id": request.state.request_id},
    )


@router.get("/forecasts/{forecast_id}")
async def get_forecast(forecast_id: UUID, request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    forecast = await service.get_forecast(forecast_id)
    return success_response(
        code="AI_FORECAST_FOUND",
        message="Detail AI forecast berhasil diambil.",
        data=AIForecastRead.model_validate(forecast),
        meta={"request_id": request.state.request_id},
    )


@router.get("/recommendations")
async def list_recommendations(request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    items = [AIRecommendationRead.model_validate(item) for item in await service.list_recommendations()]
    return success_response(
        code="AI_RECOMMENDATION_LIST_FOUND",
        message="Daftar AI recommendation berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/recommendations", status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    payload: AIRecommendationCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "finance_manager")),
) -> dict:
    service = get_ai_service(session)
    recommendation = await service.create_recommendation(payload)
    await get_audit_service(session).record_event(
        event_type="AI",
        module_name="ai",
        action_name="CREATE_RECOMMENDATION",
        summary="AI recommendation dibuat.",
        actor=actor,
        tenant_id=recommendation.tenant_id,
        sppg_id=recommendation.sppg_id,
        entity_type="ai_recommendation",
        entity_id=recommendation.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"recommendation_type": recommendation.recommendation_type, "priority": recommendation.priority},
    )
    await session.commit()
    return success_response(
        code="AI_RECOMMENDATION_CREATED",
        message="AI recommendation berhasil dibuat.",
        data=AIRecommendationRead.model_validate(recommendation),
        meta={"request_id": request.state.request_id},
    )


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(
    recommendation_id: UUID,
    request: Request,
    service: AIService = Depends(get_ai_service),
) -> dict:
    recommendation = await service.get_recommendation(recommendation_id)
    return success_response(
        code="AI_RECOMMENDATION_FOUND",
        message="Detail AI recommendation berhasil diambil.",
        data=AIRecommendationRead.model_validate(recommendation),
        meta={"request_id": request.state.request_id},
    )


@router.get("/daily-summaries")
async def list_summaries(request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    items = [AIDailySummaryRead.model_validate(item) for item in await service.list_summaries()]
    return success_response(
        code="AI_DAILY_SUMMARY_LIST_FOUND",
        message="Daftar AI daily summary berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/daily-summaries", status_code=status.HTTP_201_CREATED)
async def create_summary(
    payload: AIDailySummaryCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "finance_manager")),
) -> dict:
    service = get_ai_service(session)
    summary = await service.create_summary(payload)
    await get_audit_service(session).record_event(
        event_type="AI",
        module_name="ai",
        action_name="CREATE_DAILY_SUMMARY",
        summary="AI daily summary dibuat.",
        actor=actor,
        tenant_id=summary.tenant_id,
        sppg_id=summary.sppg_id,
        entity_type="ai_daily_summary",
        entity_id=summary.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"summary_type": summary.summary_type, "summary_date": str(summary.summary_date)},
    )
    await session.commit()
    return success_response(
        code="AI_DAILY_SUMMARY_CREATED",
        message="AI daily summary berhasil dibuat.",
        data=AIDailySummaryRead.model_validate(summary),
        meta={"request_id": request.state.request_id},
    )


@router.get("/daily-summaries/{summary_id}")
async def get_summary(summary_id: UUID, request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    summary = await service.get_summary(summary_id)
    return success_response(
        code="AI_DAILY_SUMMARY_FOUND",
        message="Detail AI daily summary berhasil diambil.",
        data=AIDailySummaryRead.model_validate(summary),
        meta={"request_id": request.state.request_id},
    )


@router.get("/overview")
async def get_overview(request: Request, service: AIService = Depends(get_ai_service)) -> dict:
    payload = await service.overview()
    return success_response(
        code="AI_OVERVIEW_FOUND",
        message="Ringkasan AI berhasil diambil.",
        data=AIOverviewRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )
