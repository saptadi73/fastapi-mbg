from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.meal_plan.models.meal_plan import MealPlan
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import MealPlanCreate
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workflow.services.workflow_service import WorkflowService
from app.support.exceptions.base import BadRequestException, NotFoundException

MEAL_PLAN_DRAFT = "DRAFT"
MEAL_PLAN_SUBMITTED = "SUBMITTED"
MEAL_PLAN_APPROVED = "APPROVED"
MEAL_PLAN_MATERIAL_RESERVED = "MATERIAL_RESERVED"


class MealPlanService:
    def __init__(
        self,
        repository: MealPlanRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        recipe_repository: RecipeRepository,
        recipe_line_repository: RecipeLineRepository,
        product_repository: ProductRepository,
        inventory_balance_repository: InventoryBalanceRepository | None = None,
        warehouse_repository: WarehouseRepository | None = None,
        workflow_service: WorkflowService | None = None,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.recipe_repository = recipe_repository
        self.recipe_line_repository = recipe_line_repository
        self.product_repository = product_repository
        self.inventory_balance_repository = inventory_balance_repository
        self.warehouse_repository = warehouse_repository
        self.workflow_service = workflow_service

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        tenant_id = None
        sppg_id = None
        current_tenant = get_current_tenant()
        current_sppg = get_current_sppg()
        if current_tenant is not None:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_TENANT_CONTEXT",
                    message="Header X-Tenant-ID tidak valid.",
                ) from exc
        if current_sppg is not None:
            try:
                sppg_id = UUID(current_sppg)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_SPPG_CONTEXT",
                    message="Header X-SPPG-ID tidak valid.",
                ) from exc
        return tenant_id, sppg_id

    async def list_meal_plans(self) -> list[MealPlan]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_meal_plan(self, meal_plan_id: UUID) -> MealPlan:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            meal_plan = await self.repository.get_by_id(meal_plan_id)
        else:
            meal_plan = await self.repository.get_by_id_and_scope(
                meal_plan_id,
                tenant_id=tenant_id,
                sppg_id=sppg_id,
            )
        if meal_plan is None:
            raise NotFoundException(code="MEAL_PLAN_NOT_FOUND", message="Meal plan tidak ditemukan.")
        return meal_plan

    async def create_meal_plan(self, payload: MealPlanCreate, actor=None) -> MealPlan:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        recipe_id = UUID(payload.recipe_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk meal plan tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG untuk meal plan tidak ditemukan.")
        recipe = await self.recipe_repository.get_by_id(recipe_id)
        if recipe is None or recipe.tenant_id != tenant_id:
            raise NotFoundException(code="RECIPE_NOT_FOUND", message="Recipe untuk meal plan tidak ditemukan.")
        meal_plan = MealPlan(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            recipe_id=recipe_id,
            plan_date=payload.plan_date,
            meal_type=payload.meal_type,
            status=payload.status,
            planned_portions=payload.planned_portions,
            budget_cost_per_portion=payload.budget_cost_per_portion,
            notes=payload.notes,
        )
        meal_plan = await self.repository.add(meal_plan)
        if self.workflow_service is not None:
            await self.workflow_service.ensure_definition_with_transitions(
                tenant_id=tenant_id,
                code="MEAL_PLAN_STANDARD",
                name="Meal Plan Approval Workflow",
                document_type="meal_plan",
                initial_state=MEAL_PLAN_DRAFT,
                transitions=[
                    {"from_state": "DRAFT", "action_name": "SUBMIT", "to_state": "SUBMITTED", "allowed_role": "operations_manager"},
                    {"from_state": "SUBMITTED", "action_name": "APPROVE", "to_state": "APPROVED", "allowed_role": "tenant_admin", "requires_approval": True},
                    {"from_state": "APPROVED", "action_name": "RESERVE_MATERIALS", "to_state": "MATERIAL_RESERVED", "allowed_role": "operations_manager"},
                ],
            )
            await self.workflow_service.ensure_instance(
                tenant_id=tenant_id,
                document_type="meal_plan",
                document_id=meal_plan.id,
                initial_state=MEAL_PLAN_DRAFT,
                actor=actor,
                notes="Meal plan dibuat.",
            )
        return meal_plan

    async def submit_meal_plan(self, meal_plan_id: UUID, actor=None) -> MealPlan:
        meal_plan = await self.get_meal_plan(meal_plan_id)
        if meal_plan.status != MEAL_PLAN_DRAFT:
            raise BadRequestException(
                code="MEAL_PLAN_SUBMIT_INVALID_STATUS",
                message="Meal plan hanya bisa disubmit dari status DRAFT.",
        )
        meal_plan.status = MEAL_PLAN_SUBMITTED
        if self.workflow_service is not None:
            await self.workflow_service.apply_transition(
                tenant_id=meal_plan.tenant_id,
                document_type="meal_plan",
                document_id=meal_plan.id,
                action_name="SUBMIT",
                expected_state=MEAL_PLAN_DRAFT,
                actor=actor,
                notes="Meal plan disubmit.",
            )
        return meal_plan

    async def approve_meal_plan(self, meal_plan_id: UUID, actor=None) -> MealPlan:
        meal_plan = await self.get_meal_plan(meal_plan_id)
        if meal_plan.status != MEAL_PLAN_SUBMITTED:
            raise BadRequestException(
                code="MEAL_PLAN_APPROVE_INVALID_STATUS",
                message="Meal plan hanya bisa diapprove dari status SUBMITTED.",
        )
        meal_plan.status = MEAL_PLAN_APPROVED
        if self.workflow_service is not None:
            await self.workflow_service.apply_transition(
                tenant_id=meal_plan.tenant_id,
                document_type="meal_plan",
                document_id=meal_plan.id,
                action_name="APPROVE",
                expected_state=MEAL_PLAN_SUBMITTED,
                actor=actor,
                notes="Meal plan diapprove.",
            )
        return meal_plan

    async def calculate_material_requirements(self, meal_plan_id: UUID) -> list[dict]:
        meal_plan = await self.get_meal_plan(meal_plan_id)
        recipe = await self.recipe_repository.get_by_id(meal_plan.recipe_id)
        if recipe is None:
            raise NotFoundException(code="RECIPE_NOT_FOUND", message="Recipe untuk meal plan tidak ditemukan.")
        recipe_lines = await self.recipe_line_repository.list_by_recipe(recipe.id)
        requirements: list[dict] = []
        for line in recipe_lines:
            product = await self.product_repository.get_by_id(line.component_product_id)
            net_quantity = line.quantity * meal_plan.planned_portions / recipe.output_quantity
            gross_quantity = net_quantity / (1 - (line.waste_percentage / 100)) if line.waste_percentage < 100 else net_quantity
            requirements.append(
                {
                    "recipe_id": str(recipe.id),
                    "component_product_id": str(line.component_product_id),
                    "component_product_code": product.code if product else None,
                    "component_product_name": product.name if product else None,
                    "planned_portions": meal_plan.planned_portions,
                    "recipe_output_quantity": recipe.output_quantity,
                    "recipe_line_quantity": line.quantity,
                    "waste_percentage": line.waste_percentage,
                    "net_quantity": round(net_quantity, 6),
                    "gross_quantity": round(gross_quantity, 6),
                    "uom_id": str(line.uom_id),
                }
            )
        return requirements

    async def reserve_materials(self, meal_plan_id: UUID) -> dict:
        if self.inventory_balance_repository is None or self.warehouse_repository is None:
            raise BadRequestException(
                code="INVENTORY_SERVICE_NOT_CONFIGURED",
                message="Layanan inventory belum dikonfigurasi untuk reservasi material.",
            )

        meal_plan = await self.get_meal_plan(meal_plan_id)
        if meal_plan.status != MEAL_PLAN_APPROVED:
            raise BadRequestException(
                code="MEAL_PLAN_RESERVE_INVALID_STATUS",
                message="Reservasi material hanya bisa dilakukan dari status APPROVED.",
            )

        requirements = await self.calculate_material_requirements(meal_plan_id)
        reserved_items: list[dict] = []

        for requirement in requirements:
            product_id = UUID(requirement["component_product_id"])
            balances = await self.inventory_balance_repository.list_by_sppg_and_product(meal_plan.sppg_id, product_id)
            required_quantity = float(requirement["gross_quantity"])
            available_total = sum(balance.quantity_available for balance in balances)
            if available_total < required_quantity:
                raise BadRequestException(
                    code="INSUFFICIENT_STOCK_FOR_MEAL_PLAN",
                    message="Stok tidak mencukupi untuk reservasi material meal plan.",
                )

            remaining = required_quantity
            for balance in balances:
                if remaining <= 0:
                    break
                reservable = min(balance.quantity_available, remaining)
                if reservable <= 0:
                    continue
                balance.quantity_reserved += reservable
                balance.quantity_available -= reservable
                remaining -= reservable
                reserved_items.append(
                    {
                        "warehouse_id": str(balance.warehouse_id),
                        "product_id": requirement["component_product_id"],
                        "product_code": requirement["component_product_code"],
                        "product_name": requirement["component_product_name"],
                        "reserved_quantity": round(reservable, 6),
                        "uom_id": requirement["uom_id"],
                    }
                )

        meal_plan.status = MEAL_PLAN_MATERIAL_RESERVED
        if self.workflow_service is not None:
            await self.workflow_service.apply_transition(
                tenant_id=meal_plan.tenant_id,
                document_type="meal_plan",
                document_id=meal_plan.id,
                action_name="RESERVE_MATERIALS",
                expected_state=MEAL_PLAN_APPROVED,
                actor=None,
                notes="Material meal plan direservasi.",
            )
        return {
            "meal_plan_id": str(meal_plan.id),
            "status": meal_plan.status,
            "reserved_items": reserved_items,
        }

    async def get_cost_preview(self, meal_plan_id: UUID) -> dict:
        meal_plan = await self.get_meal_plan(meal_plan_id)
        requirements = await self.calculate_material_requirements(meal_plan_id)
        line_items: list[dict] = []
        total_estimated_cost = 0.0

        for requirement in requirements:
            product = await self.product_repository.get_by_id(UUID(requirement["component_product_id"]))
            estimated_unit_cost = product.standard_cost if product else 0
            estimated_total_cost = round(float(requirement["gross_quantity"]) * estimated_unit_cost, 6)
            total_estimated_cost += estimated_total_cost
            line_items.append(
                {
                    "product_id": requirement["component_product_id"],
                    "product_code": requirement["component_product_code"],
                    "product_name": requirement["component_product_name"],
                    "gross_quantity": requirement["gross_quantity"],
                    "uom_id": requirement["uom_id"],
                    "estimated_unit_cost": estimated_unit_cost,
                    "estimated_total_cost": estimated_total_cost,
                }
            )

        cost_per_portion = round(total_estimated_cost / meal_plan.planned_portions, 6) if meal_plan.planned_portions > 0 else 0
        return {
            "meal_plan_id": str(meal_plan.id),
            "planned_portions": meal_plan.planned_portions,
            "currency": "IDR",
            "cost_per_portion": cost_per_portion,
            "total_estimated_cost": round(total_estimated_cost, 6),
            "line_items": line_items,
        }
