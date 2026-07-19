from datetime import datetime, timezone
from uuid import UUID

from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.schemas.stock_schema import InventoryTransactionCreate
from app.modules.inventory.services.stock_service import StockService
from app.modules.meal_plan.services.meal_plan_service import MealPlanService, MEAL_PLAN_MATERIAL_RESERVED
from app.modules.production.models.production_material_consumption import ProductionMaterialConsumption
from app.modules.production.models.production_order import ProductionOrder
from app.modules.production.repositories.production_material_consumption_repository import (
    ProductionMaterialConsumptionRepository,
)
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.product.repositories.product_repository import ProductRepository
from app.support.exceptions.base import BadRequestException, NotFoundException

PRODUCTION_PLANNED = "PLANNED"
PRODUCTION_IN_PROGRESS = "IN_PROGRESS"
PRODUCTION_COMPLETED = "COMPLETED"


class ProductionService:
    def __init__(
        self,
        production_order_repository: ProductionOrderRepository,
        production_material_repository: ProductionMaterialConsumptionRepository,
        meal_plan_service: MealPlanService,
        inventory_balance_repository: InventoryBalanceRepository,
        product_repository: ProductRepository,
        stock_service: StockService,
        accounting_service: AccountingService | None = None,
    ) -> None:
        self.production_order_repository = production_order_repository
        self.production_material_repository = production_material_repository
        self.meal_plan_service = meal_plan_service
        self.inventory_balance_repository = inventory_balance_repository
        self.product_repository = product_repository
        self.stock_service = stock_service
        self.accounting_service = accounting_service

    async def list_production_orders(self) -> list[ProductionOrder]:
        return await self.production_order_repository.list_all()

    async def get_production_order(self, production_order_id: UUID) -> ProductionOrder:
        production_order = await self.production_order_repository.get_by_id(production_order_id)
        if production_order is None:
            raise NotFoundException(code="PRODUCTION_ORDER_NOT_FOUND", message="Production order tidak ditemukan.")
        return production_order

    async def get_production_order_bundle(self, production_order_id: UUID) -> dict:
        production_order = await self.get_production_order(production_order_id)
        materials = await self.production_material_repository.list_by_production_order(production_order_id)
        return {"production_order": production_order, "materials": materials}

    async def create_from_meal_plan(self, meal_plan_id: UUID) -> dict:
        meal_plan = await self.meal_plan_service.get_meal_plan(meal_plan_id)
        if meal_plan.status != MEAL_PLAN_MATERIAL_RESERVED:
            raise BadRequestException(
                code="MEAL_PLAN_NOT_READY_FOR_PRODUCTION",
                message="Meal plan harus berstatus MATERIAL_RESERVED sebelum dibuat production order.",
            )

        next_number = await self.production_order_repository.count_by_tenant(meal_plan.tenant_id) + 1
        production_order = await self.production_order_repository.add(
            ProductionOrder(
                tenant_id=meal_plan.tenant_id,
                sppg_id=meal_plan.sppg_id,
                meal_plan_id=meal_plan.id,
                production_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                production_date=meal_plan.plan_date,
                status=PRODUCTION_PLANNED,
                planned_portions=meal_plan.planned_portions,
                actual_total_cost=0,
                actual_cost_per_portion=0,
            )
        )
        return {"production_order": production_order, "materials": []}

    async def complete_production_order(self, production_order_id: UUID, payload, actor: User) -> dict:
        production_order = await self.get_production_order(production_order_id)
        if production_order.status == PRODUCTION_COMPLETED:
            raise BadRequestException(
                code="PRODUCTION_ORDER_ALREADY_COMPLETED",
                message="Production order sudah selesai.",
            )

        meal_plan = await self.meal_plan_service.get_meal_plan(production_order.meal_plan_id)
        requirements = await self.meal_plan_service.calculate_material_requirements(meal_plan.id)
        total_actual_cost = 0.0
        created_materials: list[ProductionMaterialConsumption] = []

        production_order.status = PRODUCTION_IN_PROGRESS
        production_order.started_at = datetime.now(timezone.utc)

        for requirement in requirements:
            product_id = UUID(requirement["component_product_id"])
            required_quantity = float(requirement["gross_quantity"])
            balances = await self.inventory_balance_repository.list_by_sppg_and_product(production_order.sppg_id, product_id)
            reserved_total = sum(balance.quantity_reserved for balance in balances)
            if reserved_total < required_quantity:
                raise BadRequestException(
                    code="INSUFFICIENT_RESERVED_STOCK",
                    message="Stok reserved tidak mencukupi untuk menyelesaikan production order.",
                )

            remaining = required_quantity
            product = await self.product_repository.get_by_id(product_id)
            for balance in balances:
                if remaining <= 0:
                    break
                consumable = min(balance.quantity_reserved, remaining)
                if consumable <= 0:
                    continue
                balance.quantity_reserved -= consumable
                balance.quantity_on_hand -= consumable
                # quantity_available tetap karena stok ini sudah dikeluarkan dari available saat reserve
                unit_cost = balance.average_cost
                total_cost = round(consumable * unit_cost, 6)
                total_actual_cost += total_cost
                created_materials.append(
                    await self.production_material_repository.add(
                        ProductionMaterialConsumption(
                            tenant_id=production_order.tenant_id,
                            production_order_id=production_order.id,
                            product_id=product_id,
                            warehouse_id=balance.warehouse_id,
                            planned_quantity=required_quantity,
                            actual_quantity=round(consumable, 6),
                            uom_id=UUID(requirement["uom_id"]),
                            unit_cost=unit_cost,
                            total_cost=total_cost,
                        )
                    )
                )
                await self.stock_service.record_reserved_issue_transaction(
                    InventoryTransactionCreate(
                        tenant_id=str(production_order.tenant_id),
                        sppg_id=str(production_order.sppg_id),
                        transaction_type="ISSUE_TO_PRODUCTION",
                        reference_type="PRODUCTION_ORDER",
                        reference_id=str(production_order.id),
                        product_id=str(product_id),
                        source_warehouse_id=str(balance.warehouse_id),
                        quantity=round(consumable, 6),
                        uom_id=requirement["uom_id"],
                        unit_cost=unit_cost,
                        transaction_at=datetime.now(timezone.utc),
                        notes=f"Issue to production order {production_order.production_number} for {product.code if product else product_id}",
                    ),
                    actor,
                )
                remaining -= consumable

        production_order.actual_portions = payload.actual_portions
        production_order.accepted_portions = payload.accepted_portions
        production_order.rejected_portions = payload.rejected_portions
        production_order.completed_at = datetime.now(timezone.utc)
        production_order.status = PRODUCTION_COMPLETED
        production_order.actual_total_cost = round(total_actual_cost, 6)
        production_order.actual_cost_per_portion = (
            round(total_actual_cost / payload.accepted_portions, 6) if payload.accepted_portions > 0 else 0
        )
        meal_plan.status = "IN_PRODUCTION"
        if self.accounting_service is not None and total_actual_cost > 0:
            await self.accounting_service.create_and_post_operational_journal(
                tenant_id=production_order.tenant_id,
                entry_date=production_order.production_date,
                reference=production_order.production_number,
                description=f"Production journal {production_order.production_number}",
                source_module="production",
                source_document_type="production_order",
                source_document_id=production_order.id,
                debit_account_code="510000",
                credit_account_code="130000",
                amount=round(total_actual_cost, 6),
                actor=actor,
            )

        return {"production_order": production_order, "materials": created_materials}

    async def get_cost_sheet(self, production_order_id: UUID) -> dict:
        production_order = await self.get_production_order(production_order_id)
        materials = await self.production_material_repository.list_by_production_order(production_order_id)
        total_actual_material_cost = round(sum(item.total_cost for item in materials), 6)
        produced = production_order.actual_portions or 0
        accepted = production_order.accepted_portions or 0
        return {
            "production_order_id": str(production_order.id),
            "planned_portions": production_order.planned_portions,
            "actual_portions": production_order.actual_portions,
            "accepted_portions": production_order.accepted_portions,
            "rejected_portions": production_order.rejected_portions,
            "total_actual_material_cost": total_actual_material_cost,
            "actual_cost_per_produced_portion": round(total_actual_material_cost / produced, 6) if produced > 0 else 0,
            "actual_cost_per_accepted_portion": round(total_actual_material_cost / accepted, 6) if accepted > 0 else 0,
            "materials": [
                {
                    "product_id": str(item.product_id),
                    "warehouse_id": str(item.warehouse_id),
                    "planned_quantity": item.planned_quantity,
                    "actual_quantity": item.actual_quantity,
                    "uom_id": str(item.uom_id),
                    "unit_cost": item.unit_cost,
                    "total_cost": item.total_cost,
                }
                for item in materials
            ],
        }
