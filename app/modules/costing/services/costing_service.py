from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.costing.models.cost_policy import CostPolicy
from app.modules.costing.repositories.cost_policy_repository import CostPolicyRepository
from app.modules.costing.schemas.costing_schema import CostPolicyCreate
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.production.repositories.production_material_consumption_repository import (
    ProductionMaterialConsumptionRepository,
)
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workforce.repositories.workforce_repository import WorkforceRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class CostingService:
    def __init__(
        self,
        cost_policy_repository: CostPolicyRepository,
        production_order_repository: ProductionOrderRepository,
        production_material_repository: ProductionMaterialConsumptionRepository,
        meal_plan_repository: MealPlanRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        workforce_repository: WorkforceRepository,
    ) -> None:
        self.cost_policy_repository = cost_policy_repository
        self.production_order_repository = production_order_repository
        self.production_material_repository = production_material_repository
        self.meal_plan_repository = meal_plan_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.workforce_repository = workforce_repository

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

    async def list_cost_policies(self) -> list[CostPolicy]:
        tenant_id, sppg_id = self._get_scope()
        return await self.cost_policy_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_cost_policy(self, payload: CostPolicyCreate) -> CostPolicy:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        if payload.effective_to and payload.effective_to < payload.effective_from:
            raise BadRequestException(code="INVALID_COST_POLICY_DATE_RANGE", message="Tanggal akhir cost policy tidak valid.")
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant cost policy tidak ditemukan.")
        if sppg_id is not None:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG cost policy tidak ditemukan.")
        if await self.cost_policy_repository.get_by_tenant_code(tenant_id, payload.code) is not None:
            raise ConflictException(code="COST_POLICY_CODE_ALREADY_EXISTS", message="Kode cost policy sudah digunakan.")
        return await self.cost_policy_repository.add(
            CostPolicy(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                code=payload.code,
                name=payload.name,
                effective_from=payload.effective_from,
                effective_to=payload.effective_to,
                labor_cost_per_portion=payload.labor_cost_per_portion,
                utility_cost_per_portion=payload.utility_cost_per_portion,
                packaging_cost_per_portion=payload.packaging_cost_per_portion,
                distribution_cost_per_portion=payload.distribution_cost_per_portion,
                overhead_cost_per_portion=payload.overhead_cost_per_portion,
                waste_cost_percentage=payload.waste_cost_percentage,
                is_active=payload.is_active,
            )
        )

    async def get_production_cost_summary(self, production_order_id: UUID) -> dict:
        tenant_scope, sppg_scope = self._get_scope()
        if tenant_scope is None and sppg_scope is None:
            production_order = await self.production_order_repository.get_by_id(production_order_id)
        else:
            production_order = await self.production_order_repository.get_by_id_and_scope(
                production_order_id,
                tenant_id=tenant_scope,
                sppg_id=sppg_scope,
            )
        if production_order is None:
            raise NotFoundException(code="PRODUCTION_ORDER_NOT_FOUND", message="Production order tidak ditemukan.")
        meal_plan = await self.meal_plan_repository.get_by_id(production_order.meal_plan_id)
        if meal_plan is None:
            raise NotFoundException(code="MEAL_PLAN_NOT_FOUND", message="Meal plan untuk costing tidak ditemukan.")
        materials = await self.production_material_repository.list_by_production_order(production_order.id)
        material_cost = round(sum(item.total_cost for item in materials), 6)
        actual_portions = production_order.actual_portions or 0
        accepted_portions = production_order.accepted_portions or 0
        rejected_portions = production_order.rejected_portions or 0
        policy = await self.cost_policy_repository.get_active_policy_for_date(
            production_order.tenant_id,
            production_order.sppg_id,
            production_order.production_date,
        )
        actual_labor_cost_rows = await self.workforce_repository.list_labor_costs_by_date(
            tenant_id=production_order.tenant_id,
            sppg_id=production_order.sppg_id,
            cost_date=production_order.production_date,
        )
        actual_labor_cost = round(sum(item.total_cost for item in actual_labor_cost_rows), 6)
        if actual_labor_cost > 0:
            labor_cost = actual_labor_cost
            labor_cost_source = "ACTUAL"
        else:
            labor_cost = round((policy.labor_cost_per_portion if policy else 0) * accepted_portions, 6)
            labor_cost_source = "POLICY" if policy else "NONE"
        utility_cost = round((policy.utility_cost_per_portion if policy else 0) * accepted_portions, 6)
        packaging_cost = round((policy.packaging_cost_per_portion if policy else 0) * accepted_portions, 6)
        distribution_cost = round((policy.distribution_cost_per_portion if policy else 0) * accepted_portions, 6)
        overhead_cost = round((policy.overhead_cost_per_portion if policy else 0) * accepted_portions, 6)
        waste_cost = round(material_cost * ((policy.waste_cost_percentage if policy else 0) / 100), 6)
        total_actual_cost = round(
            material_cost + labor_cost + utility_cost + packaging_cost + distribution_cost + overhead_cost + waste_cost,
            6,
        )
        budget_cost_per_portion = round(meal_plan.budget_cost_per_portion, 6)
        budget_total = round(budget_cost_per_portion * accepted_portions, 6)
        actual_cost_per_accepted_portion = round(total_actual_cost / accepted_portions, 6) if accepted_portions > 0 else 0
        variance_total = round(total_actual_cost - budget_total, 6)
        variance_per_portion = round(actual_cost_per_accepted_portion - budget_cost_per_portion, 6)
        return {
            "production_order_id": str(production_order.id),
            "meal_plan_id": str(meal_plan.id),
            "tenant_id": str(production_order.tenant_id),
            "sppg_id": str(production_order.sppg_id),
            "applied_cost_policy_id": str(policy.id) if policy else None,
            "labor_cost_source": labor_cost_source,
            "accepted_portions": accepted_portions,
            "planned_portions": production_order.planned_portions,
            "actual_portions": actual_portions,
            "rejected_portions": rejected_portions,
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "utility_cost": utility_cost,
            "packaging_cost": packaging_cost,
            "distribution_cost": distribution_cost,
            "overhead_cost": overhead_cost,
            "waste_cost": waste_cost,
            "total_actual_cost": total_actual_cost,
            "actual_cost_per_accepted_portion": actual_cost_per_accepted_portion,
            "budget_cost_per_portion": budget_cost_per_portion,
            "budget_total_for_accepted_portions": budget_total,
            "variance_total": variance_total,
            "variance_per_portion": variance_per_portion,
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
