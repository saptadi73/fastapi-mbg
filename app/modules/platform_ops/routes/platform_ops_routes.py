from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.outbox.repository import OutboxRepository
from app.core.outbox.service import OutboxService
from app.core.security.permissions import require_roles
from app.modules.identity.models.user import User
from app.modules.platform_ops.repositories.platform_ops_repository import PlatformOpsRepository
from app.modules.platform_ops.schemas.platform_ops_schema import (
    BackgroundJobCreate,
    BackgroundJobRead,
    DailyKitchenOperationSummaryRead,
    MaterializedViewRefreshRead,
    MonthlyBudgetRealizationSummaryRead,
    OutboxEventCreate,
    OutboxEventRead,
)
from app.modules.platform_ops.services.platform_ops_service import PlatformOpsService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_platform_ops_service(session: AsyncSession = Depends(get_db_session)) -> PlatformOpsService:
    return PlatformOpsService(
        session,
        PlatformOpsRepository(session),
        TenantRepository(session),
        OutboxService(OutboxRepository(session)),
    )


@router.get("/background-jobs")
async def list_background_jobs(request: Request, service: PlatformOpsService = Depends(get_platform_ops_service), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    items = [BackgroundJobRead.model_validate(item) for item in await service.list_background_jobs()]
    return success_response(code="BACKGROUND_JOB_LIST_FOUND", message="Daftar background job berhasil diambil.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.post("/background-jobs", status_code=status.HTTP_201_CREATED)
async def create_background_job(payload: BackgroundJobCreate, request: Request, session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    item = await service.create_background_job(payload)
    await session.commit()
    return success_response(code="BACKGROUND_JOB_CREATED", message="Background job berhasil dibuat.", data=BackgroundJobRead.model_validate(item), meta={"request_id": request.state.request_id})


@router.post("/background-jobs/{job_id}/run")
async def run_background_job(job_id: UUID, request: Request, session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    result = await service.run_background_job(job_id)
    await session.commit()
    return success_response(code="BACKGROUND_JOB_RUN_COMPLETED", message="Background job berhasil dijalankan.", data=BackgroundJobRead.model_validate(result["background_job"]), meta={"request_id": request.state.request_id})


@router.get("/outbox-events")
async def list_outbox_events(request: Request, status: str | None = Query(default=None), service: PlatformOpsService = Depends(get_platform_ops_service), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    items = [OutboxEventRead.model_validate(item) for item in await service.list_outbox_events(status=status)]
    return success_response(code="OUTBOX_EVENT_LIST_FOUND", message="Daftar outbox event berhasil diambil.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.post("/outbox-events", status_code=status.HTTP_201_CREATED)
async def create_outbox_event(payload: OutboxEventCreate, request: Request, session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    item = await service.create_outbox_event(UUID(payload.tenant_id), payload.event_name, payload.aggregate_type, UUID(payload.aggregate_id) if payload.aggregate_id else None, payload.payload_json, payload.available_at)
    await session.commit()
    return success_response(code="OUTBOX_EVENT_CREATED", message="Outbox event berhasil dibuat.", data=OutboxEventRead.model_validate(item), meta={"request_id": request.state.request_id})


@router.post("/outbox-events/dispatch")
async def dispatch_outbox_events(request: Request, limit: int = Query(default=50), session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    items = [OutboxEventRead.model_validate(item) for item in await service.dispatch_outbox_events(limit=limit)]
    await session.commit()
    return success_response(code="OUTBOX_EVENT_DISPATCH_COMPLETED", message="Dispatch outbox event selesai.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.get("/read-models/daily-kitchen-operations")
async def list_daily_kitchen_operations(request: Request, summary_date: date | None = Query(default=None), service: PlatformOpsService = Depends(get_platform_ops_service), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    items = [DailyKitchenOperationSummaryRead.model_validate(item) for item in await service.list_daily_kitchen_operation_summaries(summary_date)]
    return success_response(code="DAILY_KITCHEN_OPERATION_SUMMARY_FOUND", message="Ringkasan harian dapur berhasil diambil.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.post("/read-models/daily-kitchen-operations/refresh")
async def refresh_daily_kitchen_operations(request: Request, summary_date: date | None = Query(default=None), session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    items = [DailyKitchenOperationSummaryRead.model_validate(item) for item in await service.refresh_daily_kitchen_operation_summary(summary_date)]
    await session.commit()
    return success_response(code="DAILY_KITCHEN_OPERATION_SUMMARY_REFRESHED", message="Ringkasan harian dapur berhasil direfresh.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.get("/read-models/monthly-budget-realizations")
async def list_monthly_budget_realizations(request: Request, period_month: date | None = Query(default=None), service: PlatformOpsService = Depends(get_platform_ops_service), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    items = [MonthlyBudgetRealizationSummaryRead.model_validate(item) for item in await service.list_monthly_budget_realization_summaries(period_month)]
    return success_response(code="MONTHLY_BUDGET_REALIZATION_SUMMARY_FOUND", message="Ringkasan budget bulanan berhasil diambil.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.post("/read-models/monthly-budget-realizations/refresh")
async def refresh_monthly_budget_realizations(request: Request, period_month: date | None = Query(default=None), session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    items = [MonthlyBudgetRealizationSummaryRead.model_validate(item) for item in await service.refresh_monthly_budget_realization_summary(period_month)]
    await session.commit()
    return success_response(code="MONTHLY_BUDGET_REALIZATION_SUMMARY_REFRESHED", message="Ringkasan budget bulanan berhasil direfresh.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.get("/materialized-views/delivery-performance")
async def list_delivery_performance_mv(request: Request, service: PlatformOpsService = Depends(get_platform_ops_service), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    items = await service.list_delivery_performance_materialized_view()
    return success_response(code="DELIVERY_PERFORMANCE_MV_FOUND", message="Materialized view delivery performance berhasil diambil.", data=items, meta={"request_id": request.state.request_id, "total": len(items)})


@router.post("/materialized-views/delivery-performance/refresh")
async def refresh_delivery_performance_mv(request: Request, session: AsyncSession = Depends(get_db_session), _: User = Depends(require_roles("super_admin", "tenant_admin"))) -> dict:
    service = get_platform_ops_service(session)
    items = await service.refresh_delivery_performance_materialized_view()
    await session.commit()
    return success_response(code="DELIVERY_PERFORMANCE_MV_REFRESHED", message="Materialized view delivery performance berhasil direfresh.", data=MaterializedViewRefreshRead(view_name="mv_delivery_performance_summary", refreshed=True, row_count=len(items)), meta={"request_id": request.state.request_id})
