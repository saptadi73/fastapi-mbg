from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.audit.models.audit_event import AuditEvent
from app.modules.budget.models.budget import Budget
from app.modules.budget.models.budget_line import BudgetLine
from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.document.models.document import Document
from app.modules.inventory.models.inventory_balance import InventoryBalance
from app.modules.meal_plan.models.meal_plan import MealPlan
from app.modules.production.models.production_order import ProductionOrder
from app.modules.quality.models.qc_inspection import QCInspection
from app.modules.workflow.models.workflow_instance import WorkflowInstance
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

    async def tenant_dashboard(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        meal_plan_conditions = [MealPlan.tenant_id == tenant_id] if tenant_id else []
        budget_conditions = [Budget.tenant_id == tenant_id] if tenant_id else []
        production_conditions = [ProductionOrder.tenant_id == tenant_id] if tenant_id else []
        delivery_conditions = [DeliveryOrder.tenant_id == tenant_id] if tenant_id else []
        workflow_conditions = [WorkflowInstance.tenant_id == tenant_id] if tenant_id else []
        audit_conditions = [AuditEvent.tenant_id == tenant_id] if tenant_id else []
        document_conditions = [Document.tenant_id == tenant_id] if tenant_id else []
        if sppg_id:
            meal_plan_conditions.append(MealPlan.sppg_id == sppg_id)
            production_conditions.append(ProductionOrder.sppg_id == sppg_id)
            delivery_conditions.append(DeliveryOrder.sppg_id == sppg_id)
            audit_conditions.append(AuditEvent.sppg_id == sppg_id)
            document_conditions.append(Document.sppg_id == sppg_id)

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

        return {
            "totals": {
                "meal_plans": await self._count(MealPlan, *meal_plan_conditions),
                "budgets": await self._count(Budget, *budget_conditions),
                "production_orders": await self._count(ProductionOrder, *production_conditions),
                "delivery_orders": await self._count(DeliveryOrder, *delivery_conditions),
                "documents": await self._count(Document, *document_conditions),
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
        if tenant_id:
            production_conditions.append(ProductionOrder.tenant_id == tenant_id)
            delivery_conditions.append(DeliveryOrder.tenant_id == tenant_id)
            qc_conditions.append(QCInspection.tenant_id == tenant_id)
            stock_conditions.append(InventoryBalance.tenant_id == tenant_id)
        if sppg_id:
            production_conditions.append(ProductionOrder.sppg_id == sppg_id)
            delivery_conditions.append(DeliveryOrder.sppg_id == sppg_id)
            qc_conditions.append(QCInspection.sppg_id == sppg_id)
            stock_conditions.append(InventoryBalance.sppg_id == sppg_id)

        accepted_query = select(func.coalesce(func.sum(ProductionOrder.accepted_portions), 0)).select_from(ProductionOrder)
        rejected_query = select(func.coalesce(func.sum(ProductionOrder.rejected_portions), 0)).select_from(ProductionOrder)
        received_query = select(func.coalesce(func.sum(DeliveryOrder.received_portions), 0)).select_from(DeliveryOrder)
        stock_on_hand_query = select(func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0.0)).select_from(InventoryBalance)
        stock_available_query = select(func.coalesce(func.sum(InventoryBalance.quantity_available), 0.0)).select_from(InventoryBalance)
        for condition in production_conditions:
            accepted_query = accepted_query.where(condition)
            rejected_query = rejected_query.where(condition)
        for condition in delivery_conditions:
            received_query = received_query.where(condition)
        for condition in stock_conditions:
            stock_on_hand_query = stock_on_hand_query.where(condition)
            stock_available_query = stock_available_query.where(condition)

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
