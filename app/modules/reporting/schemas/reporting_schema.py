from pydantic import BaseModel


class TenantDashboardRead(BaseModel):
    totals: dict
    statuses: dict
    finance: dict
    governance: dict


class SppgDashboardRead(BaseModel):
    totals: dict
    production: dict
    delivery: dict
    quality: dict
    stock: dict
    workforce: dict


class StockSummaryRead(BaseModel):
    totals: dict
    top_items: list[dict]


class DeliveryPerformanceRead(BaseModel):
    totals: dict
    status_breakdown: dict


class BudgetSummaryRead(BaseModel):
    totals: dict
    status_breakdown: dict


class CashFlowRead(BaseModel):
    period: dict
    totals: dict
    breakdown: list[dict]


class GovernmentReceivableAgingRead(BaseModel):
    as_of_date: str
    totals: dict
    buckets: dict
    items: list[dict]


class InvestorFundingPositionRead(BaseModel):
    as_of_date: str
    totals: dict
    items: list[dict]


class RoiBySppgRead(BaseModel):
    period: dict
    totals: dict
    items: list[dict]


class FinanceDashboardRead(BaseModel):
    as_of_date: str
    cash_flow: dict
    government_receivables: dict
    investor_funding: dict
    profitability: dict
    accounting: dict
