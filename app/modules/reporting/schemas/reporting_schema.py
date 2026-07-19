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


class StockSummaryRead(BaseModel):
    totals: dict
    top_items: list[dict]


class DeliveryPerformanceRead(BaseModel):
    totals: dict
    status_breakdown: dict


class BudgetSummaryRead(BaseModel):
    totals: dict
    status_breakdown: dict
