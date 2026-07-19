from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import (
    MealPlanCostPreviewRead,
    MealPlanCreate,
    MealPlanMaterialReservationRead,
    MealPlanRead,
)
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workflow.repositories.workflow_repository import WorkflowRepository
from app.modules.workflow.services.workflow_service import WorkflowService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_meal_plan_service(session: AsyncSession = Depends(get_db_session)) -> MealPlanService:
    return MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
        InventoryBalanceRepository(session),
        WarehouseRepository(session),
        WorkflowService(WorkflowRepository(session)),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/")
async def list_meal_plans(request: Request, service: MealPlanService = Depends(get_meal_plan_service)) -> dict:
    items = [MealPlanRead.model_validate(item) for item in await service.list_meal_plans()]
    return success_response(
        code="MEAL_PLAN_LIST_FOUND",
        message="Daftar meal plan berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{meal_plan_id}")
async def get_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
) -> dict:
    meal_plan = await service.get_meal_plan(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_FOUND",
        message="Detail meal plan berhasil diambil.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    payload: MealPlanCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = MealPlanService(
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        RecipeRepository(session),
        RecipeLineRepository(session),
        ProductRepository(session),
        workflow_service=WorkflowService(WorkflowRepository(session)),
    )
    meal_plan = await service.create_meal_plan(payload, current_user)
    await get_audit_service(session).record_event(
        event_type="OPERATIONS",
        module_name="meal_plan",
        action_name="CREATE",
        summary="Meal plan dibuat.",
        actor=current_user,
        tenant_id=meal_plan.tenant_id,
        sppg_id=meal_plan.sppg_id,
        entity_type="meal_plan",
        entity_id=meal_plan.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"plan_date": str(payload.plan_date), "planned_portions": payload.planned_portions},
    )
    await session.commit()
    return success_response(
        code="MEAL_PLAN_CREATED",
        message="Meal plan berhasil dibuat.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/calculate-requirements")
async def calculate_requirements(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    requirements = await service.calculate_material_requirements(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_REQUIREMENTS_CALCULATED",
        message="Kebutuhan bahan berhasil dihitung.",
        data=requirements,
        meta={"request_id": request.state.request_id, "total": len(requirements)},
    )


@router.post("/{meal_plan_id}/submit")
async def submit_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    meal_plan = await service.submit_meal_plan(meal_plan_id, current_user)
    await get_audit_service(session).record_event(
        event_type="APPROVAL",
        module_name="meal_plan",
        action_name="SUBMIT",
        summary="Meal plan disubmit.",
        actor=current_user,
        tenant_id=meal_plan.tenant_id,
        sppg_id=meal_plan.sppg_id,
        entity_type="meal_plan",
        entity_id=meal_plan.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()
    return success_response(
        code="MEAL_PLAN_SUBMITTED",
        message="Meal plan berhasil disubmit.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/approve")
async def approve_meal_plan(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    meal_plan = await service.approve_meal_plan(meal_plan_id, current_user)
    await get_audit_service(session).record_event(
        event_type="APPROVAL",
        module_name="meal_plan",
        action_name="APPROVE",
        summary="Meal plan diapprove.",
        actor=current_user,
        tenant_id=meal_plan.tenant_id,
        sppg_id=meal_plan.sppg_id,
        entity_type="meal_plan",
        entity_id=meal_plan.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()
    return success_response(
        code="MEAL_PLAN_APPROVED",
        message="Meal plan berhasil diapprove.",
        data=MealPlanRead.model_validate(meal_plan),
        meta={"request_id": request.state.request_id},
    )


@router.post("/{meal_plan_id}/reserve-materials")
async def reserve_materials(
    meal_plan_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_meal_plan_service(session)
    reservation = await service.reserve_materials(meal_plan_id)
    meal_plan = await service.get_meal_plan(meal_plan_id)
    await get_audit_service(session).record_event(
        event_type="INVENTORY",
        module_name="meal_plan",
        action_name="RESERVE_MATERIALS",
        summary="Material meal plan direservasi.",
        actor=current_user,
        tenant_id=meal_plan.tenant_id,
        sppg_id=meal_plan.sppg_id,
        entity_type="meal_plan",
        entity_id=UUID(reservation["meal_plan_id"]),
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"reserved_item_count": len(reservation["reserved_items"])},
    )
    await session.commit()
    return success_response(
        code="MEAL_PLAN_MATERIALS_RESERVED",
        message="Material meal plan berhasil direservasi.",
        data=MealPlanMaterialReservationRead.model_validate(reservation),
        meta={"request_id": request.state.request_id, "total": len(reservation["reserved_items"])},
    )


@router.get("/{meal_plan_id}/cost-preview")
async def get_cost_preview(
    meal_plan_id: UUID,
    request: Request,
    service: MealPlanService = Depends(get_meal_plan_service),
) -> dict:
    preview = await service.get_cost_preview(meal_plan_id)
    return success_response(
        code="MEAL_PLAN_COST_PREVIEW_FOUND",
        message="Preview biaya meal plan berhasil diambil.",
        data=MealPlanCostPreviewRead.model_validate(preview),
        meta={"request_id": request.state.request_id, "total": len(preview["line_items"])},
    )
