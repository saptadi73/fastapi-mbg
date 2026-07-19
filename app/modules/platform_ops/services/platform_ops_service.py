from datetime import UTC, date, datetime, timezone
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.outbox.models.outbox_event import OutboxEvent
from app.core.outbox.service import OutboxService
from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.budget.models.budget import Budget
from app.modules.budget.models.budget_line import BudgetLine
from app.modules.meal_plan.models.meal_plan import MealPlan
from app.modules.platform_ops.models.background_job import BackgroundJob
from app.modules.platform_ops.models.daily_kitchen_operation_summary import DailyKitchenOperationSummary
from app.modules.platform_ops.models.monthly_budget_realization_summary import MonthlyBudgetRealizationSummary
from app.modules.platform_ops.repositories.platform_ops_repository import PlatformOpsRepository
from app.modules.platform_ops.schemas.platform_ops_schema import BackgroundJobCreate
from app.modules.production.models.production_order import ProductionOrder
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.workforce.models.labor_cost import LaborCost
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException

MV_DELIVERY_PERFORMANCE = "mv_delivery_performance_summary"


class PlatformOpsService:
    def __init__(
        self,
        session: AsyncSession,
        repository: PlatformOpsRepository,
        tenant_repository: TenantRepository,
        outbox_service: OutboxService,
    ) -> None:
        self.session = session
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.outbox_service = outbox_service

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        tenant_id = UUID(get_current_tenant()) if get_current_tenant() else None
        sppg_id = UUID(get_current_sppg()) if get_current_sppg() else None
        return tenant_id, sppg_id

    async def list_background_jobs(self) -> list[BackgroundJob]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_background_jobs(tenant_id=tenant_id)

    async def create_background_job(self, payload: BackgroundJobCreate) -> BackgroundJob:
        tenant_id = UUID(payload.tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant background job tidak ditemukan.")
        if await self.repository.get_background_job_by_name(tenant_id, payload.job_name) is not None:
            raise ConflictException(code="BACKGROUND_JOB_ALREADY_EXISTS", message="Nama background job sudah digunakan.")
        return await self.repository.add_background_job(
            BackgroundJob(
                tenant_id=tenant_id,
                job_name=payload.job_name,
                job_type=payload.job_type,
                status="PENDING",
                payload_json=payload.payload_json,
                result_json={},
                scheduled_at=payload.scheduled_at,
                started_at=None,
                finished_at=None,
                notes=payload.notes,
            )
        )

    async def get_background_job(self, job_id: UUID) -> BackgroundJob:
        job = await self.repository.get_background_job_by_id(job_id)
        if job is None:
            raise NotFoundException(code="BACKGROUND_JOB_NOT_FOUND", message="Background job tidak ditemukan.")
        tenant_id, _ = self._get_scope()
        if tenant_id is not None and job.tenant_id != tenant_id:
            raise NotFoundException(code="BACKGROUND_JOB_NOT_FOUND", message="Background job tidak ditemukan.")
        return job

    async def refresh_daily_kitchen_operation_summary(self, summary_date: date | None = None) -> list[DailyKitchenOperationSummary]:
        tenant_id, sppg_scope = self._get_scope()
        target_date = summary_date or datetime.now(UTC).date()

        meal_rows = (
            await self.session.execute(
                select(MealPlan.tenant_id, MealPlan.sppg_id, func.count(MealPlan.id))
                .where(MealPlan.plan_date == target_date)
                .group_by(MealPlan.tenant_id, MealPlan.sppg_id)
            )
        ).all()
        production_rows = (
            await self.session.execute(
                select(
                    ProductionOrder.tenant_id,
                    ProductionOrder.sppg_id,
                    func.count(ProductionOrder.id),
                    func.coalesce(func.sum(ProductionOrder.accepted_portions), 0),
                    func.coalesce(func.sum(ProductionOrder.rejected_portions), 0),
                )
                .where(ProductionOrder.production_date == target_date)
                .group_by(ProductionOrder.tenant_id, ProductionOrder.sppg_id)
            )
        ).all()
        delivery_rows = (
            await self.session.execute(
                select(
                    DeliveryOrder.tenant_id,
                    DeliveryOrder.sppg_id,
                    func.count(DeliveryOrder.id),
                    func.coalesce(func.sum(DeliveryOrder.received_portions), 0),
                    func.coalesce(func.sum(DeliveryOrder.rejected_portions), 0),
                )
                .where(func.date(DeliveryOrder.planned_departure) == target_date)
                .group_by(DeliveryOrder.tenant_id, DeliveryOrder.sppg_id)
            )
        ).all()
        labor_rows = (
            await self.session.execute(
                select(LaborCost.tenant_id, LaborCost.sppg_id, func.coalesce(func.sum(LaborCost.total_cost), 0.0))
                .where(LaborCost.cost_date == target_date)
                .group_by(LaborCost.tenant_id, LaborCost.sppg_id)
            )
        ).all()

        combined: dict[tuple[UUID, UUID], dict[str, float | int]] = {}
        for tenant, sppg, count in meal_rows:
            combined.setdefault((tenant, sppg), {}).update({"meal_plan_count": int(count or 0)})
        for tenant, sppg, count, accepted, rejected in production_rows:
            combined.setdefault((tenant, sppg), {}).update(
                {
                    "production_order_count": int(count or 0),
                    "accepted_portions": int(accepted or 0),
                    "production_rejected_portions": int(rejected or 0),
                }
            )
        for tenant, sppg, count, delivered, rejected in delivery_rows:
            combined.setdefault((tenant, sppg), {}).update(
                {
                    "delivery_order_count": int(count or 0),
                    "delivered_portions": int(delivered or 0),
                    "delivery_rejected_portions": int(rejected or 0),
                }
            )
        for tenant, sppg, amount in labor_rows:
            combined.setdefault((tenant, sppg), {}).update({"labor_cost_amount": float(amount or 0.0)})

        items: list[DailyKitchenOperationSummary] = []
        for (tenant, sppg), payload in combined.items():
            if tenant_id is not None and tenant != tenant_id:
                continue
            if sppg_scope is not None and sppg != sppg_scope:
                continue
            items.append(
                DailyKitchenOperationSummary(
                    tenant_id=tenant,
                    sppg_id=sppg,
                    summary_date=target_date,
                    meal_plan_count=int(payload.get("meal_plan_count", 0)),
                    production_order_count=int(payload.get("production_order_count", 0)),
                    delivery_order_count=int(payload.get("delivery_order_count", 0)),
                    accepted_portions=int(payload.get("accepted_portions", 0)),
                    delivered_portions=int(payload.get("delivered_portions", 0)),
                    rejected_portions=int(payload.get("delivery_rejected_portions", payload.get("production_rejected_portions", 0))),
                    labor_cost_amount=round(float(payload.get("labor_cost_amount", 0.0)), 6),
                    refresh_source="SUMMARY_TABLE",
                )
            )

        await self.repository.replace_daily_kitchen_summaries(
            summary_date=target_date,
            tenant_id=tenant_id,
            sppg_id=sppg_scope,
            items=items,
        )
        return await self.repository.list_daily_kitchen_summaries(target_date, tenant_id, sppg_scope)

    async def list_daily_kitchen_operation_summaries(self, summary_date: date | None = None) -> list[DailyKitchenOperationSummary]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_daily_kitchen_summaries(summary_date=summary_date, tenant_id=tenant_id, sppg_id=sppg_id)

    async def refresh_monthly_budget_realization_summary(self, period_month: date | None = None) -> list[MonthlyBudgetRealizationSummary]:
        tenant_id, _ = self._get_scope()
        target_month = (period_month or datetime.now(UTC).date().replace(day=1)).replace(day=1)
        rows = (
            await self.session.execute(
                select(
                    Budget.tenant_id,
                    func.count(Budget.id),
                    func.coalesce(func.sum(func.coalesce(BudgetLine.revised_amount, BudgetLine.planned_amount)), 0.0),
                    func.coalesce(func.sum(BudgetLine.cached_reserved_amount), 0.0),
                    func.coalesce(func.sum(BudgetLine.cached_committed_amount), 0.0),
                    func.coalesce(func.sum(BudgetLine.cached_actual_amount), 0.0),
                )
                .select_from(BudgetLine)
                .join(Budget, Budget.id == BudgetLine.budget_id)
                .where(extract("year", Budget.date_start) == target_month.year)
                .where(extract("month", Budget.date_start) == target_month.month)
                .group_by(Budget.tenant_id)
            )
        ).all()
        items = [
            MonthlyBudgetRealizationSummary(
                tenant_id=row[0],
                period_month=target_month,
                budgets_count=int(row[1] or 0),
                effective_budget=round(float(row[2] or 0.0), 6),
                reserved_amount=round(float(row[3] or 0.0), 6),
                committed_amount=round(float(row[4] or 0.0), 6),
                actual_amount=round(float(row[5] or 0.0), 6),
                refresh_source="SUMMARY_TABLE",
            )
            for row in rows
            if tenant_id is None or row[0] == tenant_id
        ]
        await self.repository.replace_monthly_budget_summaries(period_month=target_month, tenant_id=tenant_id, items=items)
        return await self.repository.list_monthly_budget_summaries(period_month=target_month, tenant_id=tenant_id)

    async def list_monthly_budget_realization_summaries(self, period_month: date | None = None) -> list[MonthlyBudgetRealizationSummary]:
        tenant_id, _ = self._get_scope()
        target_month = period_month.replace(day=1) if period_month else None
        return await self.repository.list_monthly_budget_summaries(period_month=target_month, tenant_id=tenant_id)

    async def refresh_delivery_performance_materialized_view(self) -> list[dict]:
        await self.repository.refresh_materialized_view(MV_DELIVERY_PERFORMANCE)
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.fetch_materialized_view_rows(MV_DELIVERY_PERFORMANCE, tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_delivery_performance_materialized_view(self) -> list[dict]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.fetch_materialized_view_rows(MV_DELIVERY_PERFORMANCE, tenant_id=tenant_id, sppg_id=sppg_id)

    async def list_outbox_events(self, status: str | None = None) -> list[OutboxEvent]:
        tenant_id, _ = self._get_scope()
        return await self.outbox_service.list_events(tenant_id=tenant_id, status=status)

    async def create_outbox_event(self, tenant_id: UUID, event_name: str, aggregate_type: str, aggregate_id: UUID | None, payload_json: dict, available_at: datetime | None = None) -> OutboxEvent:
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant outbox event tidak ditemukan.")
        return await self.outbox_service.create_event(
            tenant_id=tenant_id,
            event_name=event_name,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload_json=payload_json,
            available_at=available_at,
        )

    async def dispatch_outbox_events(self, limit: int = 50) -> list[OutboxEvent]:
        tenant_id, _ = self._get_scope()
        return await self.outbox_service.dispatch_pending(tenant_id=tenant_id, limit=limit)

    async def run_background_job(self, job_id: UUID) -> dict:
        job = await self.get_background_job(job_id)
        job.status = "RUNNING"
        job.started_at = datetime.now(timezone.utc)
        if job.job_type == "REFRESH_DAILY_KITCHEN_OPERATION_SUMMARY":
            rows = await self.refresh_daily_kitchen_operation_summary(
                date.fromisoformat(job.payload_json["summary_date"]) if job.payload_json.get("summary_date") else None
            )
            job.result_json = {"row_count": len(rows), "summary_type": "daily_kitchen_operation_summary"}
        elif job.job_type == "REFRESH_MONTHLY_BUDGET_REALIZATION_SUMMARY":
            rows = await self.refresh_monthly_budget_realization_summary(
                date.fromisoformat(job.payload_json["period_month"]) if job.payload_json.get("period_month") else None
            )
            job.result_json = {"row_count": len(rows), "summary_type": "monthly_budget_realization_summary"}
        elif job.job_type == "REFRESH_MV_DELIVERY_PERFORMANCE_SUMMARY":
            rows = await self.refresh_delivery_performance_materialized_view()
            job.result_json = {"row_count": len(rows), "view_name": MV_DELIVERY_PERFORMANCE}
        elif job.job_type == "DISPATCH_OUTBOX":
            events = await self.dispatch_outbox_events(limit=int(job.payload_json.get("limit", 50)))
            job.result_json = {"event_count": len(events)}
        else:
            raise BadRequestException(code="BACKGROUND_JOB_TYPE_UNSUPPORTED", message="Jenis background job belum didukung.")
        job.status = "SUCCESS"
        job.finished_at = datetime.now(timezone.utc)
        return {"background_job": job}
