from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.modules.reporting.schemas.reporting_schema import (
    BalanceSheetRead,
    BudgetSummaryRead,
    CashFlowRead,
    DeliveryPerformanceRead,
    FinanceDashboardRead,
    GovernmentReceivableAgingRead,
    InvestorFundingPositionRead,
    ProfitLossRead,
    RoiBySppgRead,
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


@router.get("/finance/cash-flow")
async def get_cash_flow(
    request: Request,
    period_start: date | None = None,
    period_end: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.cash_flow(period_start=period_start, period_end=period_end)
    return success_response(
        code="REPORTING_CASH_FLOW_FOUND",
        message="Laporan cash flow berhasil diambil.",
        data=CashFlowRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["breakdown"])},
    )


@router.get("/finance/profit-loss")
async def get_profit_loss(
    request: Request,
    period_start: date | None = None,
    period_end: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.profit_loss(period_start=period_start, period_end=period_end)
    return success_response(
        code="REPORTING_PROFIT_LOSS_FOUND",
        message="Laporan laba rugi berhasil diambil.",
        data=ProfitLossRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["expenses"]["categories"])},
    )


@router.get("/finance/balance-sheet")
async def get_balance_sheet(
    request: Request,
    as_of_date: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.balance_sheet(as_of_date=as_of_date)
    return success_response(
        code="REPORTING_BALANCE_SHEET_FOUND",
        message="Laporan neraca berhasil diambil.",
        data=BalanceSheetRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/finance/government-receivable-aging")
async def get_government_receivable_aging(
    request: Request,
    as_of_date: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.government_receivable_aging(as_of_date=as_of_date)
    return success_response(
        code="REPORTING_GOVERNMENT_RECEIVABLE_AGING_FOUND",
        message="Laporan aging piutang pemerintah berhasil diambil.",
        data=GovernmentReceivableAgingRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/finance/investor-funding-position")
async def get_investor_funding_position(
    request: Request,
    as_of_date: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.investor_funding_position(as_of_date=as_of_date)
    return success_response(
        code="REPORTING_INVESTOR_FUNDING_POSITION_FOUND",
        message="Laporan posisi pendanaan investor berhasil diambil.",
        data=InvestorFundingPositionRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/finance/roi-by-sppg")
async def get_roi_by_sppg(
    request: Request,
    period_start: date | None = None,
    period_end: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.roi_by_sppg(period_start=period_start, period_end=period_end)
    return success_response(
        code="REPORTING_ROI_BY_SPPG_FOUND",
        message="Laporan ROI per SPPG berhasil diambil.",
        data=RoiBySppgRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/dashboard/finance")
async def get_finance_dashboard(
    request: Request,
    as_of_date: date | None = None,
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    payload = await service.finance_dashboard(as_of_date=as_of_date)
    return success_response(
        code="REPORTING_FINANCE_DASHBOARD_FOUND",
        message="Dashboard finance berhasil diambil.",
        data=FinanceDashboardRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )
