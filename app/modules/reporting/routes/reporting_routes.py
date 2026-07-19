from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.modules.reporting.schemas.reporting_schema import (
    BudgetSummaryRead,
    DeliveryPerformanceRead,
    SppgDashboardRead,
    StockSummaryRead,
    TenantDashboardRead,
)
from app.modules.reporting.services.reporting_service import ReportingService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_reporting_service(session: AsyncSession = Depends(get_db_session)) -> ReportingService:
    return ReportingService(session)


@router.get("/dashboard/tenant")
async def get_tenant_dashboard(request: Request, service: ReportingService = Depends(get_reporting_service)) -> dict:
    payload = await service.tenant_dashboard()
    return success_response(
        code="REPORTING_TENANT_DASHBOARD_FOUND",
        message="Dashboard tenant berhasil diambil.",
        data=TenantDashboardRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/dashboard/sppg")
async def get_sppg_dashboard(request: Request, service: ReportingService = Depends(get_reporting_service)) -> dict:
    payload = await service.sppg_dashboard()
    return success_response(
        code="REPORTING_SPPG_DASHBOARD_FOUND",
        message="Dashboard SPPG berhasil diambil.",
        data=SppgDashboardRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/stock-summary")
async def get_stock_summary(request: Request, service: ReportingService = Depends(get_reporting_service)) -> dict:
    payload = await service.stock_summary()
    return success_response(
        code="REPORTING_STOCK_SUMMARY_FOUND",
        message="Ringkasan stok berhasil diambil.",
        data=StockSummaryRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["top_items"])},
    )


@router.get("/delivery-performance")
async def get_delivery_performance(request: Request, service: ReportingService = Depends(get_reporting_service)) -> dict:
    payload = await service.delivery_performance()
    return success_response(
        code="REPORTING_DELIVERY_PERFORMANCE_FOUND",
        message="Ringkasan performa delivery berhasil diambil.",
        data=DeliveryPerformanceRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/budget-summary")
async def get_budget_summary(request: Request, service: ReportingService = Depends(get_reporting_service)) -> dict:
    payload = await service.budget_summary()
    return success_response(
        code="REPORTING_BUDGET_SUMMARY_FOUND",
        message="Ringkasan budget berhasil diambil.",
        data=BudgetSummaryRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )
