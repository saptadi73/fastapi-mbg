from datetime import date
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.platform_ops.models.background_job import BackgroundJob
from app.modules.platform_ops.models.daily_kitchen_operation_summary import DailyKitchenOperationSummary
from app.modules.platform_ops.models.monthly_budget_realization_summary import MonthlyBudgetRealizationSummary


class PlatformOpsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_background_jobs(self, tenant_id: UUID | None = None) -> list[BackgroundJob]:
        query = select(BackgroundJob).order_by(BackgroundJob.created_at.desc())
        if tenant_id is not None:
            query = query.where(BackgroundJob.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_background_job_by_id(self, job_id: UUID) -> BackgroundJob | None:
        return await self.session.get(BackgroundJob, job_id)

    async def get_background_job_by_name(self, tenant_id: UUID, job_name: str) -> BackgroundJob | None:
        result = await self.session.execute(
            select(BackgroundJob).where(BackgroundJob.tenant_id == tenant_id, BackgroundJob.job_name == job_name)
        )
        return result.scalar_one_or_none()

    async def add_background_job(self, job: BackgroundJob) -> BackgroundJob:
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job

    async def list_daily_kitchen_summaries(
        self,
        summary_date: date | None = None,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> list[DailyKitchenOperationSummary]:
        query = select(DailyKitchenOperationSummary).order_by(
            DailyKitchenOperationSummary.summary_date.desc(),
            DailyKitchenOperationSummary.sppg_id,
        )
        if summary_date is not None:
            query = query.where(DailyKitchenOperationSummary.summary_date == summary_date)
        if tenant_id is not None:
            query = query.where(DailyKitchenOperationSummary.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(DailyKitchenOperationSummary.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def replace_daily_kitchen_summaries(
        self,
        *,
        summary_date: date,
        tenant_id: UUID | None,
        sppg_id: UUID | None,
        items: list[DailyKitchenOperationSummary],
    ) -> None:
        stmt = delete(DailyKitchenOperationSummary).where(DailyKitchenOperationSummary.summary_date == summary_date)
        if tenant_id is not None:
            stmt = stmt.where(DailyKitchenOperationSummary.tenant_id == tenant_id)
        if sppg_id is not None:
            stmt = stmt.where(DailyKitchenOperationSummary.sppg_id == sppg_id)
        await self.session.execute(stmt)
        self.session.add_all(items)
        await self.session.flush()

    async def list_monthly_budget_summaries(
        self,
        period_month: date | None = None,
        tenant_id: UUID | None = None,
    ) -> list[MonthlyBudgetRealizationSummary]:
        query = select(MonthlyBudgetRealizationSummary).order_by(MonthlyBudgetRealizationSummary.period_month.desc())
        if period_month is not None:
            query = query.where(MonthlyBudgetRealizationSummary.period_month == period_month)
        if tenant_id is not None:
            query = query.where(MonthlyBudgetRealizationSummary.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def replace_monthly_budget_summaries(
        self,
        *,
        period_month: date,
        tenant_id: UUID | None,
        items: list[MonthlyBudgetRealizationSummary],
    ) -> None:
        stmt = delete(MonthlyBudgetRealizationSummary).where(MonthlyBudgetRealizationSummary.period_month == period_month)
        if tenant_id is not None:
            stmt = stmt.where(MonthlyBudgetRealizationSummary.tenant_id == tenant_id)
        await self.session.execute(stmt)
        self.session.add_all(items)
        await self.session.flush()

    async def refresh_materialized_view(self, view_name: str) -> None:
        await self.session.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))

    async def fetch_materialized_view_rows(self, view_name: str, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[dict]:
        filters = []
        params: dict[str, object] = {}
        if tenant_id is not None:
            filters.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id
        if sppg_id is not None:
            filters.append("sppg_id = :sppg_id")
            params["sppg_id"] = sppg_id
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        rows = (await self.session.execute(text(f"SELECT * FROM {view_name} {where_clause} ORDER BY tenant_id, sppg_id, status"), params)).mappings().all()
        return [dict(row) for row in rows]
