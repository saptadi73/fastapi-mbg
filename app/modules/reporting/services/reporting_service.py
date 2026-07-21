from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.account import Account
from app.modules.accounting.models.journal_entry import JournalEntry
from app.modules.accounting.models.journal_line import JournalLine
from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.audit.models.audit_event import AuditEvent
from app.modules.budget.models.budget import Budget
from app.modules.budget.models.budget_line import BudgetLine
from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.document.models.document import Document
from app.modules.funding.models.funding_agreement import FundingAgreement
from app.modules.funding.models.funding_disbursement import FundingDisbursement
from app.modules.funding.models.funding_repayment import FundingRepayment
from app.modules.funding.models.funding_source import FundingSource
from app.modules.government_claim.models.government_claim import GovernmentClaim
from app.modules.inventory.models.inventory_balance import InventoryBalance
from app.modules.meal_plan.models.meal_plan import MealPlan
from app.modules.production.models.production_order import ProductionOrder
from app.modules.quality.models.qc_inspection import QCInspection
from app.modules.sppg.models.sppg import Sppg
from app.modules.workflow.models.workflow_instance import WorkflowInstance
from app.modules.workforce.models.attendance import Attendance
from app.modules.workforce.models.employee import Employee
from app.modules.workforce.models.labor_cost import LaborCost
from app.support.exceptions.base import BadRequestException


class ReportingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def _count(self, model, *conditions) -> int:
        query = select(func.count()).select_from(model)
        for condition in conditions:
            query = query.where(condition)
        result = await self.session.execute(query)
        return int(result.scalar_one() or 0)

    @staticmethod
    def _default_as_of_date() -> date:
        return datetime.now(timezone.utc).date()

    @staticmethod
    def _bucket_days(days: int) -> str:
        if days <= 30:
            return "0_30"
        if days <= 60:
            return "31_60"
        if days <= 90:
            return "61_90"
        return "90_plus"

    async def tenant_dashboard(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        meal_plan_conditions = [MealPlan.tenant_id == tenant_id] if tenant_id else []
        budget_conditions = [Budget.tenant_id == tenant_id] if tenant_id else []
        production_conditions = [ProductionOrder.tenant_id == tenant_id] if tenant_id else []
        delivery_conditions = [DeliveryOrder.tenant_id == tenant_id] if tenant_id else []
        workflow_conditions = [WorkflowInstance.tenant_id == tenant_id] if tenant_id else []
        audit_conditions = [AuditEvent.tenant_id == tenant_id] if tenant_id else []
        document_conditions = [Document.tenant_id == tenant_id] if tenant_id else []
        workforce_employee_conditions = [Employee.tenant_id == tenant_id] if tenant_id else []
        labor_cost_conditions = [LaborCost.tenant_id == tenant_id] if tenant_id else []
        if sppg_id:
            meal_plan_conditions.append(MealPlan.sppg_id == sppg_id)
            production_conditions.append(ProductionOrder.sppg_id == sppg_id)
            delivery_conditions.append(DeliveryOrder.sppg_id == sppg_id)
            audit_conditions.append(AuditEvent.sppg_id == sppg_id)
            document_conditions.append(Document.sppg_id == sppg_id)
            labor_cost_conditions.append(LaborCost.sppg_id == sppg_id)

        approved_budget_amount_query = select(
            func.coalesce(
                func.sum(
                    func.coalesce(BudgetLine.revised_amount, BudgetLine.planned_amount)
                ),
                0.0,
            )
        ).select_from(BudgetLine).join(Budget, Budget.id == BudgetLine.budget_id)
        if tenant_id:
            approved_budget_amount_query = approved_budget_amount_query.where(Budget.tenant_id == tenant_id)
        approved_budget_amount_query = approved_budget_amount_query.where(Budget.status == "APPROVED")
        approved_budget_amount = float((await self.session.execute(approved_budget_amount_query)).scalar_one() or 0.0)

        actual_budget_amount_query = select(
            func.coalesce(func.sum(BudgetLine.cached_actual_amount), 0.0)
        ).select_from(BudgetLine).join(Budget, Budget.id == BudgetLine.budget_id)
        if tenant_id:
            actual_budget_amount_query = actual_budget_amount_query.where(Budget.tenant_id == tenant_id)
        actual_budget_amount = float((await self.session.execute(actual_budget_amount_query)).scalar_one() or 0.0)

        labor_cost_query = select(func.coalesce(func.sum(LaborCost.total_cost), 0.0)).select_from(LaborCost)
        for condition in labor_cost_conditions:
            labor_cost_query = labor_cost_query.where(condition)
        actual_labor_cost_amount = float((await self.session.execute(labor_cost_query)).scalar_one() or 0.0)

        return {
            "totals": {
                "meal_plans": await self._count(MealPlan, *meal_plan_conditions),
                "budgets": await self._count(Budget, *budget_conditions),
                "production_orders": await self._count(ProductionOrder, *production_conditions),
                "delivery_orders": await self._count(DeliveryOrder, *delivery_conditions),
                "documents": await self._count(Document, *document_conditions),
                "employees": await self._count(Employee, *workforce_employee_conditions),
            },
            "statuses": {
                "meal_plan_approved": await self._count(MealPlan, *meal_plan_conditions, MealPlan.status == "APPROVED"),
                "meal_plan_material_reserved": await self._count(MealPlan, *meal_plan_conditions, MealPlan.status == "MATERIAL_RESERVED"),
                "budget_approved": await self._count(Budget, *budget_conditions, Budget.status == "APPROVED"),
                "delivery_received": await self._count(DeliveryOrder, *delivery_conditions, DeliveryOrder.status == "RECEIVED"),
            },
            "finance": {
                "approved_budget_amount": round(approved_budget_amount, 6),
                "actual_budget_amount": round(actual_budget_amount, 6),
                "actual_labor_cost_amount": round(actual_labor_cost_amount, 6),
            },
            "governance": {
                "workflow_instances": await self._count(WorkflowInstance, *workflow_conditions),
                "audit_events": await self._count(AuditEvent, *audit_conditions),
            },
        }

    async def sppg_dashboard(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        production_conditions = []
        delivery_conditions = []
        qc_conditions = []
        stock_conditions = []
        labor_conditions = []
        attendance_conditions = []
        if tenant_id:
            production_conditions.append(ProductionOrder.tenant_id == tenant_id)
            delivery_conditions.append(DeliveryOrder.tenant_id == tenant_id)
            qc_conditions.append(QCInspection.tenant_id == tenant_id)
            stock_conditions.append(InventoryBalance.tenant_id == tenant_id)
            labor_conditions.append(LaborCost.tenant_id == tenant_id)
            attendance_conditions.append(Attendance.tenant_id == tenant_id)
        if sppg_id:
            production_conditions.append(ProductionOrder.sppg_id == sppg_id)
            delivery_conditions.append(DeliveryOrder.sppg_id == sppg_id)
            qc_conditions.append(QCInspection.sppg_id == sppg_id)
            stock_conditions.append(InventoryBalance.sppg_id == sppg_id)
            labor_conditions.append(LaborCost.sppg_id == sppg_id)
            attendance_conditions.append(Attendance.sppg_id == sppg_id)

        accepted_query = select(func.coalesce(func.sum(ProductionOrder.accepted_portions), 0)).select_from(ProductionOrder)
        rejected_query = select(func.coalesce(func.sum(ProductionOrder.rejected_portions), 0)).select_from(ProductionOrder)
        received_query = select(func.coalesce(func.sum(DeliveryOrder.received_portions), 0)).select_from(DeliveryOrder)
        stock_on_hand_query = select(func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0.0)).select_from(InventoryBalance)
        stock_available_query = select(func.coalesce(func.sum(InventoryBalance.quantity_available), 0.0)).select_from(InventoryBalance)
        labor_cost_query = select(func.coalesce(func.sum(LaborCost.total_cost), 0.0)).select_from(LaborCost)
        attendance_hours_query = select(func.coalesce(func.sum(Attendance.worked_hours), 0.0)).select_from(Attendance)
        for condition in production_conditions:
            accepted_query = accepted_query.where(condition)
            rejected_query = rejected_query.where(condition)
        for condition in delivery_conditions:
            received_query = received_query.where(condition)
        for condition in stock_conditions:
            stock_on_hand_query = stock_on_hand_query.where(condition)
            stock_available_query = stock_available_query.where(condition)
        for condition in labor_conditions:
            labor_cost_query = labor_cost_query.where(condition)
        for condition in attendance_conditions:
            attendance_hours_query = attendance_hours_query.where(condition)

        return {
            "totals": {
                "production_orders": await self._count(ProductionOrder, *production_conditions),
                "delivery_orders": await self._count(DeliveryOrder, *delivery_conditions),
                "qc_inspections": await self._count(QCInspection, *qc_conditions),
            },
            "production": {
                "completed_orders": await self._count(ProductionOrder, *production_conditions, ProductionOrder.status == "COMPLETED"),
                "accepted_portions": int((await self.session.execute(accepted_query)).scalar_one() or 0),
                "rejected_portions": int((await self.session.execute(rejected_query)).scalar_one() or 0),
            },
            "delivery": {
                "received_orders": await self._count(DeliveryOrder, *delivery_conditions, DeliveryOrder.status == "RECEIVED"),
                "partially_received_orders": await self._count(DeliveryOrder, *delivery_conditions, DeliveryOrder.status == "PARTIALLY_RECEIVED"),
                "received_portions": int((await self.session.execute(received_query)).scalar_one() or 0),
            },
            "quality": {
                "passed_inspections": await self._count(QCInspection, *qc_conditions, QCInspection.status == "PASSED"),
                "failed_inspections": await self._count(QCInspection, *qc_conditions, QCInspection.status == "FAILED"),
            },
            "stock": {
                "quantity_on_hand": round(float((await self.session.execute(stock_on_hand_query)).scalar_one() or 0.0), 6),
                "quantity_available": round(float((await self.session.execute(stock_available_query)).scalar_one() or 0.0), 6),
            },
            "workforce": {
                "attendance_records": await self._count(Attendance, *attendance_conditions),
                "worked_hours": round(float((await self.session.execute(attendance_hours_query)).scalar_one() or 0.0), 6),
                "labor_cost_amount": round(float((await self.session.execute(labor_cost_query)).scalar_one() or 0.0), 6),
            },
        }

    async def stock_summary(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        total_query = select(
            func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0.0),
            func.coalesce(func.sum(InventoryBalance.quantity_reserved), 0.0),
            func.coalesce(func.sum(InventoryBalance.quantity_available), 0.0),
        ).select_from(InventoryBalance)
        top_query = select(
            InventoryBalance.product_id,
            func.sum(InventoryBalance.quantity_on_hand).label("quantity_on_hand"),
            func.sum(InventoryBalance.quantity_available).label("quantity_available"),
        ).group_by(InventoryBalance.product_id).order_by(func.sum(InventoryBalance.quantity_on_hand).desc()).limit(5)
        if tenant_id:
            total_query = total_query.where(InventoryBalance.tenant_id == tenant_id)
            top_query = top_query.where(InventoryBalance.tenant_id == tenant_id)
        if sppg_id:
            total_query = total_query.where(InventoryBalance.sppg_id == sppg_id)
            top_query = top_query.where(InventoryBalance.sppg_id == sppg_id)
        totals = (await self.session.execute(total_query)).one()
        top_rows = (await self.session.execute(top_query)).all()
        return {
            "totals": {
                "quantity_on_hand": round(float(totals[0] or 0.0), 6),
                "quantity_reserved": round(float(totals[1] or 0.0), 6),
                "quantity_available": round(float(totals[2] or 0.0), 6),
            },
            "top_items": [
                {
                    "product_id": str(row.product_id),
                    "quantity_on_hand": round(float(row.quantity_on_hand or 0.0), 6),
                    "quantity_available": round(float(row.quantity_available or 0.0), 6),
                }
                for row in top_rows
            ],
        }

    async def delivery_performance(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        conditions = []
        if tenant_id:
            conditions.append(DeliveryOrder.tenant_id == tenant_id)
        if sppg_id:
            conditions.append(DeliveryOrder.sppg_id == sppg_id)
        shipped_query = select(func.coalesce(func.sum(DeliveryOrder.shipped_portions), 0)).select_from(DeliveryOrder)
        received_query = select(func.coalesce(func.sum(DeliveryOrder.received_portions), 0)).select_from(DeliveryOrder)
        rejected_query = select(func.coalesce(func.sum(DeliveryOrder.rejected_portions), 0)).select_from(DeliveryOrder)
        for condition in conditions:
            shipped_query = shipped_query.where(condition)
            received_query = received_query.where(condition)
            rejected_query = rejected_query.where(condition)
        return {
            "totals": {
                "delivery_orders": await self._count(DeliveryOrder, *conditions),
                "shipped_portions": int((await self.session.execute(shipped_query)).scalar_one() or 0),
                "received_portions": int((await self.session.execute(received_query)).scalar_one() or 0),
                "rejected_portions": int((await self.session.execute(rejected_query)).scalar_one() or 0),
            },
            "status_breakdown": {
                "in_transit": await self._count(DeliveryOrder, *conditions, DeliveryOrder.status == "IN_TRANSIT"),
                "received": await self._count(DeliveryOrder, *conditions, DeliveryOrder.status == "RECEIVED"),
                "partially_received": await self._count(DeliveryOrder, *conditions, DeliveryOrder.status == "PARTIALLY_RECEIVED"),
                "rejected": await self._count(DeliveryOrder, *conditions, DeliveryOrder.status == "REJECTED"),
            },
        }

    async def budget_summary(self) -> dict:
        tenant_id, _ = self._get_scope()
        budget_conditions = [Budget.tenant_id == tenant_id] if tenant_id else []
        totals_query = select(
            func.coalesce(func.sum(func.coalesce(BudgetLine.revised_amount, BudgetLine.planned_amount)), 0.0),
            func.coalesce(func.sum(BudgetLine.cached_reserved_amount), 0.0),
            func.coalesce(func.sum(BudgetLine.cached_committed_amount), 0.0),
            func.coalesce(func.sum(BudgetLine.cached_actual_amount), 0.0),
        ).select_from(BudgetLine).join(Budget, Budget.id == BudgetLine.budget_id)
        for condition in budget_conditions:
            totals_query = totals_query.where(condition)
        totals = (await self.session.execute(totals_query)).one()
        return {
            "totals": {
                "effective_budget": round(float(totals[0] or 0.0), 6),
                "reserved_amount": round(float(totals[1] or 0.0), 6),
                "committed_amount": round(float(totals[2] or 0.0), 6),
                "actual_amount": round(float(totals[3] or 0.0), 6),
            },
            "status_breakdown": {
                "draft": await self._count(Budget, *budget_conditions, Budget.status == "DRAFT"),
                "submitted": await self._count(Budget, *budget_conditions, Budget.status == "SUBMITTED"),
                "approved": await self._count(Budget, *budget_conditions, Budget.status == "APPROVED"),
            },
        }

    async def cash_flow(self, period_start: date | None = None, period_end: date | None = None) -> dict:
        tenant_id, _ = self._get_scope()
        query = (
            select(
                JournalEntry.source_module,
                JournalEntry.source_document_type,
                func.coalesce(
                    func.sum(case((JournalLine.line_type == "DEBIT", JournalLine.amount), else_=0.0)),
                    0.0,
                ).label("cash_in"),
                func.coalesce(
                    func.sum(case((JournalLine.line_type == "CREDIT", JournalLine.amount), else_=0.0)),
                    0.0,
                ).label("cash_out"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalEntry.id == JournalLine.journal_entry_id)
            .join(Account, Account.id == JournalLine.account_id)
            .where(JournalEntry.status == "POSTED")
            .where(Account.category == "ASSET")
            .where(Account.code.like("11%"))
            .group_by(JournalEntry.source_module, JournalEntry.source_document_type)
            .order_by(JournalEntry.source_module, JournalEntry.source_document_type)
        )
        if tenant_id:
            query = query.where(JournalEntry.tenant_id == tenant_id)
        if period_start:
            query = query.where(JournalEntry.entry_date >= period_start)
        if period_end:
            query = query.where(JournalEntry.entry_date <= period_end)
        rows = (await self.session.execute(query)).all()
        breakdown = []
        total_inflow = 0.0
        total_outflow = 0.0
        for row in rows:
            cash_in = round(float(row.cash_in or 0.0), 6)
            cash_out = round(float(row.cash_out or 0.0), 6)
            breakdown.append(
                {
                    "source_module": row.source_module,
                    "source_document_type": row.source_document_type,
                    "cash_in": cash_in,
                    "cash_out": cash_out,
                    "net_cash_flow": round(cash_in - cash_out, 6),
                }
            )
            total_inflow += cash_in
            total_outflow += cash_out
        return {
            "period": {
                "start_date": str(period_start) if period_start else None,
                "end_date": str(period_end) if period_end else None,
            },
            "totals": {
                "cash_in": round(total_inflow, 6),
                "cash_out": round(total_outflow, 6),
                "net_cash_flow": round(total_inflow - total_outflow, 6),
            },
            "breakdown": breakdown,
        }

    async def government_receivable_aging(self, as_of_date: date | None = None) -> dict:
        tenant_id, sppg_id = self._get_scope()
        as_of = as_of_date or self._default_as_of_date()
        query = select(GovernmentClaim).order_by(GovernmentClaim.period_end, GovernmentClaim.claim_number)
        if tenant_id:
            query = query.where(GovernmentClaim.tenant_id == tenant_id)
        if sppg_id:
            query = query.where(GovernmentClaim.sppg_id == sppg_id)
        claims = list((await self.session.execute(query)).scalars().all())
        items: list[dict] = []
        bucket_totals = {"0_30": 0.0, "31_60": 0.0, "61_90": 0.0, "90_plus": 0.0}
        total_outstanding = 0.0
        overdue_amount = 0.0
        for claim in claims:
            base_amount = float(claim.approved_amount if claim.approved_amount is not None else claim.claimed_amount)
            outstanding = round(base_amount - float(claim.paid_amount or 0.0), 6)
            if outstanding <= 0:
                continue
            reference_date = claim.verified_at or claim.submitted_at or claim.period_end
            days_outstanding = max((as_of - reference_date).days, 0)
            bucket = self._bucket_days(days_outstanding)
            bucket_totals[bucket] = round(bucket_totals[bucket] + outstanding, 6)
            total_outstanding = round(total_outstanding + outstanding, 6)
            if days_outstanding > 30:
                overdue_amount = round(overdue_amount + outstanding, 6)
            items.append(
                {
                    "claim_id": str(claim.id),
                    "claim_number": claim.claim_number,
                    "sppg_id": str(claim.sppg_id) if claim.sppg_id else None,
                    "status": claim.status,
                    "period_start": str(claim.period_start),
                    "period_end": str(claim.period_end),
                    "reference_date": str(reference_date),
                    "approved_amount": round(base_amount, 6),
                    "paid_amount": round(float(claim.paid_amount or 0.0), 6),
                    "outstanding_amount": outstanding,
                    "days_outstanding": days_outstanding,
                    "aging_bucket": bucket,
                }
            )
        return {
            "as_of_date": str(as_of),
            "totals": {
                "open_claims": len(items),
                "outstanding_amount": total_outstanding,
                "overdue_amount": overdue_amount,
            },
            "buckets": bucket_totals,
            "items": items,
        }

    async def investor_funding_position(self, as_of_date: date | None = None) -> dict:
        tenant_id, sppg_id = self._get_scope()
        as_of = as_of_date or self._default_as_of_date()
        source_query = select(FundingSource).where(FundingSource.source_type.like("INVESTOR%"))
        if tenant_id:
            source_query = source_query.where(FundingSource.tenant_id == tenant_id)
        investor_sources = list((await self.session.execute(source_query)).scalars().all())
        source_ids = {item.id for item in investor_sources}
        if not source_ids:
            return {
                "as_of_date": str(as_of),
                "totals": {
                    "agreements": 0,
                    "principal_committed": 0.0,
                    "principal_disbursed": 0.0,
                    "principal_repaid": 0.0,
                    "outstanding_principal": 0.0,
                    "realized_margin": 0.0,
                },
                "items": [],
            }
        agreement_query = select(FundingAgreement).where(FundingAgreement.funding_source_id.in_(source_ids))
        if tenant_id:
            agreement_query = agreement_query.where(FundingAgreement.tenant_id == tenant_id)
        agreements = list((await self.session.execute(agreement_query)).scalars().all())
        items: list[dict] = []
        totals = {
            "agreements": 0,
            "principal_committed": 0.0,
            "principal_disbursed": 0.0,
            "principal_repaid": 0.0,
            "outstanding_principal": 0.0,
            "realized_margin": 0.0,
        }
        source_map = {item.id: item for item in investor_sources}
        for agreement in agreements:
            disb_query = select(FundingDisbursement).where(FundingDisbursement.agreement_id == agreement.id)
            if sppg_id:
                disb_query = disb_query.where(FundingDisbursement.sppg_id == sppg_id)
            disbursements = list((await self.session.execute(disb_query)).scalars().all())
            repayments = list(
                (
                    await self.session.execute(
                        select(FundingRepayment).where(FundingRepayment.agreement_id == agreement.id)
                    )
                ).scalars().all()
            )
            principal_disbursed = round(sum(float(item.amount or 0.0) for item in disbursements), 6)
            principal_repaid = round(sum(float(item.principal_amount or 0.0) for item in repayments), 6)
            realized_margin = round(sum(float(item.margin_amount or 0.0) for item in repayments), 6)
            outstanding = round(principal_disbursed - principal_repaid, 6)
            source = source_map.get(agreement.funding_source_id)
            items.append(
                {
                    "agreement_id": str(agreement.id),
                    "funding_source_id": str(agreement.funding_source_id),
                    "source_name": source.name if source else None,
                    "source_type": source.source_type if source else None,
                    "party_name": source.party_name if source else None,
                    "agreement_type": agreement.agreement_type,
                    "status": agreement.status,
                    "principal_amount": round(float(agreement.principal_amount or 0.0), 6),
                    "principal_disbursed": principal_disbursed,
                    "principal_repaid": principal_repaid,
                    "outstanding_principal": outstanding,
                    "realized_margin": realized_margin,
                    "margin_rate": round(float(agreement.margin_rate or 0.0), 6) if agreement.margin_rate is not None else None,
                }
            )
            totals["agreements"] += 1
            totals["principal_committed"] += round(float(agreement.principal_amount or 0.0), 6)
            totals["principal_disbursed"] += principal_disbursed
            totals["principal_repaid"] += principal_repaid
            totals["outstanding_principal"] += outstanding
            totals["realized_margin"] += realized_margin
        for key, value in totals.items():
            if key != "agreements":
                totals[key] = round(float(value), 6)
        return {"as_of_date": str(as_of), "totals": totals, "items": items}

    async def roi_by_sppg(self, period_start: date | None = None, period_end: date | None = None) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        sppg_query = select(Sppg).order_by(Sppg.name)
        if tenant_id:
            sppg_query = sppg_query.where(Sppg.tenant_id == tenant_id)
        if sppg_scope:
            sppg_query = sppg_query.where(Sppg.id == sppg_scope)
        sppg_rows = list((await self.session.execute(sppg_query)).scalars().all())

        prod_query = select(ProductionOrder)
        claim_query = select(GovernmentClaim)
        delivery_query = select(DeliveryOrder)
        disbursement_query = select(FundingDisbursement)
        repayment_query = select(FundingRepayment)
        if tenant_id:
            prod_query = prod_query.where(ProductionOrder.tenant_id == tenant_id)
            claim_query = claim_query.where(GovernmentClaim.tenant_id == tenant_id)
            delivery_query = delivery_query.where(DeliveryOrder.tenant_id == tenant_id)
            disbursement_query = disbursement_query.where(FundingDisbursement.tenant_id == tenant_id)
            repayment_query = repayment_query.where(FundingRepayment.tenant_id == tenant_id)
        if sppg_scope:
            prod_query = prod_query.where(ProductionOrder.sppg_id == sppg_scope)
            claim_query = claim_query.where(GovernmentClaim.sppg_id == sppg_scope)
            delivery_query = delivery_query.where(DeliveryOrder.sppg_id == sppg_scope)
            disbursement_query = disbursement_query.where(FundingDisbursement.sppg_id == sppg_scope)
        if period_start:
            prod_query = prod_query.where(ProductionOrder.production_date >= period_start)
            claim_query = claim_query.where(GovernmentClaim.period_end >= period_start)
            delivery_query = delivery_query.where(func.date(DeliveryOrder.planned_departure) >= period_start)
            disbursement_query = disbursement_query.where(FundingDisbursement.disbursement_date >= period_start)
            repayment_query = repayment_query.where(FundingRepayment.repayment_date >= period_start)
        if period_end:
            prod_query = prod_query.where(ProductionOrder.production_date <= period_end)
            claim_query = claim_query.where(GovernmentClaim.period_start <= period_end)
            delivery_query = delivery_query.where(func.date(DeliveryOrder.planned_departure) <= period_end)
            disbursement_query = disbursement_query.where(FundingDisbursement.disbursement_date <= period_end)
            repayment_query = repayment_query.where(FundingRepayment.repayment_date <= period_end)

        productions = list((await self.session.execute(prod_query)).scalars().all())
        claims = list((await self.session.execute(claim_query)).scalars().all())
        deliveries = list((await self.session.execute(delivery_query)).scalars().all())
        disbursements = list((await self.session.execute(disbursement_query)).scalars().all())
        repayments = list((await self.session.execute(repayment_query)).scalars().all())

        production_by_sppg: dict[UUID, dict[str, float]] = {}
        for item in productions:
            bucket = production_by_sppg.setdefault(item.sppg_id, {"production_cost": 0.0, "accepted_portions": 0.0})
            bucket["production_cost"] += float(item.actual_total_cost or 0.0)
            bucket["accepted_portions"] += float(item.accepted_portions or 0.0)

        claim_by_sppg: dict[UUID, dict[str, float]] = {}
        for item in claims:
            if item.sppg_id is None:
                continue
            bucket = claim_by_sppg.setdefault(item.sppg_id, {"recognized_revenue": 0.0, "cash_collected": 0.0})
            bucket["recognized_revenue"] += float(item.approved_amount if item.approved_amount is not None else item.claimed_amount or 0.0)
            bucket["cash_collected"] += float(item.paid_amount or 0.0)

        delivery_by_sppg: dict[UUID, dict[str, float]] = {}
        for item in deliveries:
            bucket = delivery_by_sppg.setdefault(item.sppg_id, {"received_portions": 0.0, "delivery_orders": 0.0})
            bucket["received_portions"] += float(item.received_portions or 0.0)
            bucket["delivery_orders"] += 1.0

        disb_by_agreement_sppg: dict[UUID, dict[UUID, float]] = {}
        for item in disbursements:
            if item.sppg_id is None:
                continue
            disb_by_agreement_sppg.setdefault(item.agreement_id, {})
            disb_by_agreement_sppg[item.agreement_id][item.sppg_id] = round(
                disb_by_agreement_sppg[item.agreement_id].get(item.sppg_id, 0.0) + float(item.amount or 0.0),
                6,
            )

        finance_cost_by_sppg: dict[UUID, float] = {}
        repayment_by_agreement: dict[UUID, float] = {}
        for item in repayments:
            repayment_by_agreement[item.agreement_id] = round(
                repayment_by_agreement.get(item.agreement_id, 0.0) + float(item.margin_amount or 0.0) + float(item.penalty_amount or 0.0),
                6,
            )
        for agreement_id, sppg_amounts in disb_by_agreement_sppg.items():
            total_disbursed = sum(sppg_amounts.values())
            finance_cost = repayment_by_agreement.get(agreement_id, 0.0)
            if total_disbursed <= 0 or finance_cost <= 0:
                continue
            for sppg_id, disbursed_amount in sppg_amounts.items():
                allocated = round((disbursed_amount / total_disbursed) * finance_cost, 6)
                finance_cost_by_sppg[sppg_id] = round(finance_cost_by_sppg.get(sppg_id, 0.0) + allocated, 6)

        items: list[dict] = []
        total_revenue = 0.0
        total_cost = 0.0
        for sppg in sppg_rows:
            production_payload = production_by_sppg.get(sppg.id, {})
            claim_payload = claim_by_sppg.get(sppg.id, {})
            delivery_payload = delivery_by_sppg.get(sppg.id, {})
            production_cost = round(float(production_payload.get("production_cost", 0.0)), 6)
            financing_cost = round(float(finance_cost_by_sppg.get(sppg.id, 0.0)), 6)
            recognized_revenue = round(float(claim_payload.get("recognized_revenue", 0.0)), 6)
            total_operating_cost = round(production_cost + financing_cost, 6)
            gross_surplus = round(recognized_revenue - total_operating_cost, 6)
            roi_percent = round((gross_surplus / total_operating_cost) * 100, 6) if total_operating_cost > 0 else 0.0
            items.append(
                {
                    "sppg_id": str(sppg.id),
                    "sppg_code": sppg.code,
                    "sppg_name": sppg.name,
                    "accepted_portions": int(production_payload.get("accepted_portions", 0.0) or 0),
                    "received_portions": int(delivery_payload.get("received_portions", 0.0) or 0),
                    "delivery_orders": int(delivery_payload.get("delivery_orders", 0.0) or 0),
                    "recognized_revenue": recognized_revenue,
                    "cash_collected": round(float(claim_payload.get("cash_collected", 0.0)), 6),
                    "production_cost": production_cost,
                    "financing_cost": financing_cost,
                    "total_cost": total_operating_cost,
                    "gross_surplus": gross_surplus,
                    "roi_percent": roi_percent,
                }
            )
            total_revenue = round(total_revenue + recognized_revenue, 6)
            total_cost = round(total_cost + total_operating_cost, 6)
        average_roi = round(sum(item["roi_percent"] for item in items) / len(items), 6) if items else 0.0
        return {
            "period": {
                "start_date": str(period_start) if period_start else None,
                "end_date": str(period_end) if period_end else None,
            },
            "totals": {
                "sppg_count": len(items),
                "recognized_revenue": total_revenue,
                "total_cost": total_cost,
                "gross_surplus": round(total_revenue - total_cost, 6),
                "average_roi_percent": average_roi,
            },
            "items": items,
        }

    async def finance_dashboard(self, as_of_date: date | None = None) -> dict:
        as_of = as_of_date or self._default_as_of_date()
        cash_flow = await self.cash_flow(period_end=as_of)
        receivables = await self.government_receivable_aging(as_of)
        funding = await self.investor_funding_position(as_of)
        roi = await self.roi_by_sppg(period_end=as_of)
        tenant_id, _ = self._get_scope()
        accounting_conditions = [JournalEntry.tenant_id == tenant_id] if tenant_id else []
        return {
            "as_of_date": str(as_of),
            "cash_flow": cash_flow["totals"],
            "government_receivables": {
                "open_claims": receivables["totals"]["open_claims"],
                "outstanding_amount": receivables["totals"]["outstanding_amount"],
                "overdue_amount": receivables["totals"]["overdue_amount"],
            },
            "investor_funding": {
                "agreements": funding["totals"]["agreements"],
                "outstanding_principal": funding["totals"]["outstanding_principal"],
                "realized_margin": funding["totals"]["realized_margin"],
            },
            "profitability": {
                "sppg_count": roi["totals"]["sppg_count"],
                "recognized_revenue": roi["totals"]["recognized_revenue"],
                "gross_surplus": roi["totals"]["gross_surplus"],
                "average_roi_percent": roi["totals"]["average_roi_percent"],
                "top_sppg": max(roi["items"], key=lambda item: item["roi_percent"], default=None),
            },
            "accounting": {
                "posted_journal_entries": await self._count(JournalEntry, *accounting_conditions, JournalEntry.status == "POSTED"),
            },
        }
